'''views.py'''
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from .models import Project
from .forms import ProjectForm


def project_list(request):
    """Главная страница со списком проектов"""
    # pylint: disable=no-member
    projects = Project.objects.filter(status='open').order_by('-created_at')

    paginator = Paginator(projects, 12)
    page_number = request.GET.get('page', 1)
    projects_page = paginator.get_page(page_number)

    context = {
        'page_obj': projects_page,
        'is_paginated': projects_page.has_other_pages(),
    }
    return render(request, 'projects/project_list.html', context)


def project_detail(request, project_id):
    """Страница проекта"""
    project = get_object_or_404(Project, id=project_id)
    user_is_participant = (request.user.is_authenticated
                           and request.user in project.participants.all())
    user_is_owner = request.user.is_authenticated and request.user == project.owner
    is_favorited = request.user.is_authenticated and project in request.user.favorites.all()

    context = {
        'project': project,
        'user_is_participant': user_is_participant,
        'user_is_owner': user_is_owner,
        'is_favorited': is_favorited,
    }
    return render(request, 'projects/project-details.html', context)


@login_required
@require_http_methods(['POST'])
def toggle_favorite(request, project_id):
    """Добавление/удаление из избранного"""
    project = get_object_or_404(Project, id=project_id)

    if project in request.user.favorites.all():
        request.user.favorites.remove(project)
        favorited = False
    else:
        request.user.favorites.add(project)
        favorited = True

    return JsonResponse({'status': 'ok', 'favorited': favorited})


@login_required
def favorite_projects(request):
    """Страница избранных проектов"""
    projects = request.user.favorites.all()

    paginator = Paginator(projects, 12)
    page_number = request.GET.get('page', 1)
    projects_page = paginator.get_page(page_number)

    context = {'projects': projects_page}
    return render(request, 'projects/favorite_projects.html', context)


@login_required
@require_http_methods(['POST'])
def complete_project(request, project_id):
    """Завершение проекта"""
    project = get_object_or_404(Project, id=project_id, owner=request.user)

    if project.status == 'open':
        project.status = 'closed'
        project.save()
        return JsonResponse({'status': 'ok', 'project_status': 'closed'})

    return JsonResponse({'status': 'error', 'message': 'Проект уже завершён'}, status=400)


@login_required
@require_http_methods(['POST'])
def toggle_participate(request, project_id):
    """Присоединение/отказ от участия в проекте"""
    project = get_object_or_404(Project, id=project_id)

    # Нельзя участвовать в своём проекте
    if request.user == project.owner:
        return JsonResponse({
            'status': 'error',
            'message': 'Вы автор проекта'
        }, status=400)

    # Добавляем или удаляем участника
    if request.user in project.participants.all():
        project.participants.remove(request.user)
        participated = False
    else:
        project.participants.add(request.user)
        participated = True

    # Генерируем HTML для списка участников
    participants_html = ''
    for member in project.participants.all():
        avatar_url = member.avatar.url if member.avatar else '/static/images/default-avatar.png'
        participants_html += f'''
        <a href="/users/{member.id}" id="participant-{member.id}">
            <div class="participant-item">
                <img src="{avatar_url}" alt="Аватар" class="participant-avatar">
                <div class="participant-info">
                    <span class="participant-name">{member.name} {member.surname}</span>
                    <span class="participant-role">
                        {"Автор проекта" if member.id == project.owner.id else "Участник"}
                    </span>
                </div>
            </div>
        </a>
        '''

    if not participants_html:
        participants_html = '<p id="no-participants">Пока нет участников</p>'

    return JsonResponse({
        'status': 'ok',
        'participated': participated,
        'participants_count': project.participants.count(),
        'participants_html': participants_html
    })


@login_required
def create_project(request):
    """Создание проекта"""
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            project.participants.add(request.user)  # Автор автоматически участник
            return redirect('projects:project_detail', project_id=project.id)
    else:
        form = ProjectForm()

    return render(request, 'projects/create-project.html', {
        'form': form,
        'is_edit': False
    })


@login_required
def edit_project(request, project_id):
    """Редактирование проекта"""
    project = get_object_or_404(Project, id=project_id, owner=request.user)

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect('projects:project_detail', project_id=project.id)
    else:
        form = ProjectForm(instance=project)

    return render(request, 'projects/create-project.html', {
        'form': form,
        'is_edit': True,
        'project': project
    })

'''Представления для управления пользователями.'''
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from projects.models import Project
from .models import User
from .forms import RegistrationForm, LoginForm, EditProfileForm, CustomPasswordChangeForm


def register_view(request):
    """Регистрация пользователя"""
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            return redirect('projects:project_list')
    else:
        form = RegistrationForm()

    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    """Вход в систему"""
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user:
                login(request, user)
                return redirect('projects:project_list')
            form.add_error(None, 'Неверный имейл или пароль')
    else:
        form = LoginForm()

    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    """Выход из системы"""
    logout(request)
    return redirect('projects:project_list')


def user_detail(request, user_id):
    """Страница пользователя"""
    user_profile = get_object_or_404(User, id=user_id)
    # pylint: disable=no-member
    user_projects = Project.objects.filter(owner=user_profile)
    is_owner = request.user.is_authenticated and request.user == user_profile

    context = {
        'user': user_profile,  # Шаблон ожидает 'user'
        'user_projects': user_projects,
        'is_owner': is_owner,
    }
    return render(request, 'users/user-details.html', context)


@login_required
def edit_profile(request):
    """Редактирование профиля"""
    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save(commit=False)

            if not user.phone or user.phone.strip() == '':
                user.phone = None
            user.save()
            messages.success(request, 'Профиль успешно обновлён')
            return redirect('users:user_detail', user_id=request.user.id)
    else:
        form = EditProfileForm(instance=request.user)

    return render(request, 'users/edit_profile.html', {'form': form})


@login_required
def change_password(request):
    """Смена пароля"""
    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Пароль успешно изменён')
            return redirect('users:user_detail', user_id=request.user.id)
    else:
        form = CustomPasswordChangeForm(user=request.user)

    return render(request, 'users/change_password.html', {'form': form})


def user_list(request):
    """Список пользователей с фильтрацией"""
    users = User.objects.filter(is_active=True).order_by('id')
    active_filter = request.GET.get('filter')

    if request.user.is_authenticated and active_filter:
        if active_filter == 'owners-of-favorite-projects':
            # Авторы избранных проектов
            favorite_projects = request.user.favorites.all()
            users = User.objects.filter(owned_projects__in=favorite_projects).distinct()
            print(f"DEBUG: Найдено авторов избранных проектов: {users.count()}")

        elif active_filter == 'owners-of-participating-projects':
            # Авторы проектов, в которых я участвую
            users = User.objects.filter(
                owned_projects__in=request.user.participated_projects.all()).distinct()
            print(f"DEBUG: Найдено авторов проектов, в которых я участвую: {users.count()}")

        elif active_filter == 'interested-in-my-projects':
            # Пользователи, которым нравятся мои проекты
            my_projects = request.user.owned_projects.all()
            users = User.objects.filter(favorites__in=my_projects).distinct()
            print(f"DEBUG: Найдено пользователей, которым нравятся мои проекты: {users.count()}")

        elif active_filter == 'participants-of-my-projects':
            # Участники моих проектов
            my_projects = request.user.owned_projects.all()
            users = User.objects.filter(participated_projects__in=my_projects).distinct()
            print(f"DEBUG: Найдено участников моих проектов: {users.count()}")

    paginator = Paginator(users, 12)
    page_number = request.GET.get('page', 1)
    users_page = paginator.get_page(page_number)
    query_prefix = f"filter={active_filter}&" if active_filter else ""

    context = {
        'page_obj': users_page,
        'active_filter': active_filter,
        'query_prefix': query_prefix,
        'filters': {
            'owners-of-favorite-projects': 'Авторы избранных проектов',
            'owners-of-participating-projects': 'Авторы проектов, в которых я участвую',
            'interested-in-my-projects': 'Пользователи, которым нравятся мои проекты',
            'participants-of-my-projects': 'Участники моих проектов',
        }
    }
    return render(request, 'users/participants.html', context)

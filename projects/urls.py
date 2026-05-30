'''urls.py'''
from django.urls import path
from . import views

# pylint: disable=invalid-name
app_name = 'projects'

urlpatterns = [
    path('list/', views.project_list, name='project_list'),
    path('<int:project_id>/', views.project_detail, name='project_detail'),
    path('<int:project_id>/toggle-favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('<int:project_id>/complete/', views.complete_project, name='complete_project'),
    path('<int:project_id>/toggle-participate/', views.toggle_participate,
         name='toggle_participate'),
    path('<int:project_id>/edit/', views.edit_project, name='edit_project'),
    path('favorites/', views.favorite_projects, name='favorite_projects'),
    path('create-project/', views.create_project, name='create_project'),
]

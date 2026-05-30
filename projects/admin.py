'''admin.py'''
from django.contrib import admin
from .models import Project

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    '''Настройки админки'''
    list_display = ['name', 'owner', 'created_at', 'status']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'owner__email', 'owner__name', 'owner__surname']
    readonly_fields = ['created_at']

    fieldsets = (
        (None, {'fields': ('name', 'description', 'owner', 'status')}),
        ('Ссылки', {'fields': ('github_url',)}),
        ('Участники', {'fields': ('participants',)}),
        ('Даты', {'fields': ('created_at',)}),
    )

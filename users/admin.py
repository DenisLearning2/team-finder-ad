'''Admin configuration for the User model.'''
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


class CustomUserAdmin(UserAdmin):
    '''Настройка отображения модели User в админке'''
    model = User
    list_display = ['email', 'name', 'surname', 'phone', 'is_staff']
    list_filter = ['is_staff', 'is_active', 'created_at']
    readonly_fields = ['created_at']
    search_fields = ['email', 'name', 'surname', 'phone']
    ordering = ['-created_at']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Личная информация', {'fields': ('name', 'surname', 'avatar', 'phone',
                                          'github_url', 'about')}),
        ('Избранное', {'fields': ('favorites',)}),
        ('Права доступа', {'fields': ('is_active', 'is_staff', 'is_superuser',
                                      'groups', 'user_permissions')}),
        ('Даты', {'fields': ('last_login', 'created_at')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'surname', 'phone', 'password1',
                       'password2', 'is_staff', 'is_active')}
        ),
    )

admin.site.register(User, CustomUserAdmin)

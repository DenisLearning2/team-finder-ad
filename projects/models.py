'''models.py'''
from django.db import models
from django.conf import settings
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError


def validate_github_url(value):
    """Проверяет, что ссылка ведёт на GitHub"""
    if value and value.strip():
        URLValidator()(value)
        if 'github.com' not in value.lower():
            raise ValidationError('Ссылка должна вести на GitHub')


class Project(models.Model):
    '''Модель проекта'''
    STATUS_CHOICES = [
        ('открыт', 'Открыт'),
        ('закрыт', 'Закрыт'),
    ]

    name = models.CharField(max_length=200, verbose_name='Название проекта')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_projects',
        verbose_name='Автор'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    github_url = models.URLField(blank=True, null=True, validators=[validate_github_url],
                                 verbose_name='Ссылка на GitHub')
    status = models.CharField(max_length=6, choices=STATUS_CHOICES, default='open',
                              verbose_name='Статус')
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='participated_projects',
        blank=True,
        verbose_name='Участники'
    )

    def __str__(self):
        return str(self.name)

    # pylint: disable=too-few-public-methods
    class Meta:
        '''Class Meta'''
        ordering = ['-created_at']

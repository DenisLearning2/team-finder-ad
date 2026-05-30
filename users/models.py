'''Модель пользователя с расширенными полями и функционалом генерации аватарки.'''
import random
from io import BytesIO

from django.core.files.base import ContentFile
from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from PIL import Image, ImageDraw, ImageFont

class UserManager(BaseUserManager):
    '''Менеджер для модели User, обеспечивающий создание пользователей и суперпользователей.'''
    def create_user(self, email, name, surname, password=None, **extra_fields):
        '''Создает и сохраняет пользователя с указанным email, именем, фамилией и паролем.'''
        if not email:
            raise ValueError('Email обязателен')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, surname=surname, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, surname, password=None, **extra_fields):
        '''Создает и сохраняет суперпользователя с указанным email, именем, фамилией и паролем.'''
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, name, surname, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    '''Модель пользователя с расширенными полями и функционалом генерации аватарки.'''
    COLORS = [
        '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
        '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E2',
        '#FFB347', '#5D9B9B', '#E8A0BF', '#A7C7E7', '#FFD966'
    ]

    email = models.EmailField(unique=True, verbose_name='Email')
    name = models.CharField(max_length=124, verbose_name='Имя')
    surname = models.CharField(max_length=124, verbose_name='Фамилия')
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.jpg',
                               verbose_name='Аватар')
    phone = models.CharField(
        max_length=12,
        unique=True,
        null=True,
        blank=True,
        validators=[RegexValidator(r'^\+7\d{10}$',
                                   'Номер должен быть в формате +7XXXXXXXXXX (10 цифр после +7)')],
        verbose_name='Телефон'
    )
    github_url = models.URLField(blank=True, null=True, verbose_name='GitHub')
    about = models.TextField(max_length=256, blank=True, null=True, verbose_name='О себе')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    favorites = models.ManyToManyField(
        'projects.Project',
        related_name='interested_users',
        blank=True,
        verbose_name='Избранные проекты'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'surname']

    objects = UserManager()

    def save(self, *args, **kwargs):
        # Приводим телефон к формату +7XXXXXXXXXX
        if self.phone:
            if self.phone.startswith('8'):
                self.phone = '+7' + self.phone[1:]

        # Генерируем аватарку если её нет или это дефолтная
        if not self.avatar or not self.avatar.name or self.avatar.name == 'avatars/default.jpg':
            self.avatar = self.generate_avatar()

        super().save(*args, **kwargs)

    def generate_avatar(self):
        """Генерирует аватарку с первой буквой имени на цветном фоне"""
        size = (200, 200)
        image = Image.new('RGB', size, self.get_random_color())
        draw = ImageDraw.Draw(image)

        # Буква для отображения
        if self.name and isinstance(self.name, str):
            letter = str(self.name)[0].upper() if str(self.name)[0] else '?'
        else:
            letter = '?'

        # Пытаемся загрузить шрифт
        font = None
        try:
            # Для Linux/Mac
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 100)
        except (OSError, IOError):
            try:
                # Для Windows
                font = ImageFont.truetype("arial.ttf", 100)
            except (OSError, IOError):
                font = ImageFont.load_default()

        # Получаем размер текста
        bbox = draw.textbbox((0, 0), letter, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Центрируем текст
        x = (size[0] - text_width) // 2
        y = (size[1] - text_height) // 2

        draw.text((x, y), letter, fill='white', font=font)

        # Сохраняем в BytesIO
        buffer = BytesIO()
        image.save(buffer, format='PNG')
        buffer.seek(0)

        return ContentFile(buffer.read(), name=f'avatar_{str(self.email).replace("@", "_")}.png')

    def get_random_color(self):
        '''Выбирает случайный цвет из предопределенного списка.'''
        return random.choice(self.COLORS)

    def get_full_name(self):
        '''Возвращает полное имя пользователя.'''
        return f'{self.name} {self.surname}'

    def __str__(self):
        return self.get_full_name()

'''Forms for user registration, login, profile editing, and password change.'''
from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from .models import User


class RegistrationForm(forms.ModelForm):
    '''Form for user registration.'''
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Пароль'
    )

    # pylint: disable=too-few-public-methods
    class Meta:
        '''Meta class for RegistrationForm.'''
        model = User
        fields = ['name', 'surname', 'email', 'password']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'surname': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean_email(self):
        '''Validate that the email is unique.'''
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже существует')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.phone = None
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    '''Form for user login.'''
    email = forms.EmailField(label='Email')
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')


class EditProfileForm(forms.ModelForm):
    '''Form for editing user profile.'''
    avatar = forms.ImageField(
        label='Аватар',
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )

    # pylint: disable=too-few-public-methods
    class Meta:
        '''Meta class for EditProfileForm.'''
        model = User
        fields = ['name', 'surname', 'avatar', 'about', 'phone', 'github_url']
        widgets = {
            'about': forms.Textarea(attrs={'rows': 4,
                                           'class': 'w-full px-3 py-2 border rounded-lg'}),
            'name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg'}),
            'surname': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg'}),
            'phone': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg'}),
            'github_url': forms.URLInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg'}),
        }

    def clean_phone(self):
        '''Validate and normalize the phone number.'''
        phone = self.cleaned_data.get('phone')
        instance = getattr(self, 'instance', None)

        if not phone or phone.strip() == '':
            return None

        phone = phone.replace(' ', '').replace('(', '').replace(')', '')

        if phone.startswith('8'):
            if len(phone) != 11:
                raise forms.ValidationError(
                    'Номер телефона должен содержать 11 цифр в формате 8ХХХХХХХХХХ')
            phone = '+7' + phone[1:]
        elif phone.startswith('+7'):
            if len(phone) != 12:
                raise forms.ValidationError(
                    'Номер телефона должен содержать 12 символов в формате +7ХХХХХХХХХХ')
        else:
            raise forms.ValidationError('Номер телефона должен начинаться с 8 или +7')

        if not phone[2:].isdigit():
            raise forms.ValidationError(
                'Номер телефона должен содержать только цифры после кода страны')

        if instance and instance.pk:
            if User.objects.filter(phone=phone).exclude(pk=instance.pk).exists():
                raise forms.ValidationError('ПОльзователь с таким номером телефона уже существует')
        else:
            if User.objects.filter(phone=phone).exists():
                raise forms.ValidationError('Пользователь с таким номером телефона уже существует')

        return phone

    # pylint: disable=duplicate-code
    def clean_github_url(self):
        '''Validate the GitHub URL.'''
        url = self.cleaned_data.get('github_url')
        if url and url.strip():
            if 'github.com' not in url.lower():
                raise forms.ValidationError('Ссылка должна вести на GitHub')
        return url


class CustomPasswordChangeForm(PasswordChangeForm):
    '''Form for changing user password.'''
    old_password = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'w-full px-3 py-2 border rounded-lg'}), label='Старый пароль')
    new_password1 = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'w-full px-3 py-2 border rounded-lg'}), label='Новый пароль')
    new_password2 = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'w-full px-3 py-2 border rounded-lg'}), label='Подтверждение пароля')

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Login",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your login',
            'id': 'id_username'
        })
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '**********',
            'id': 'id_password'
        })
    )

    error_messages = {
        'invalid_login': "Incorrect login or password"
    }


class SignUpForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].validators = []
        self.fields['password2'].validators = []

    email = forms.EmailField(
        max_length=50,
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'drpepper@mail.ru'
        })
    )
    nickname = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Dr. Pepper'
        })
    )
    avatar = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'dr_peeper'
            }),
            'password1': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': '********'
            }),
            'password2': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': '********'
            }),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This login is already in use")
        return username

    def clean_nickname(self):
        nickname = self.cleaned_data.get('nickname')
        if Profile.objects.filter(nickname=nickname).exists():
            raise forms.ValidationError("This nickname is already in use")
        return nickname

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if len(password1) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long")
        return password1

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            profile = Profile.objects.create(
                user=user,
                nickname=self.cleaned_data['nickname'],
                login=user.username
            )
            if self.cleaned_data['avatar']:
                profile.avatar = self.cleaned_data['avatar']
                profile.save()
        return user

class LogoutForm(forms.Form):
    pass


class SettingsForm(forms.ModelForm):
    email = forms.EmailField(
        max_length=50,
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'id': 'id_email'
        })
    )
    nickname = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'id_nickname'
        })
    )
    avatar = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
            'id': 'id_avatar'
        })
    )

    class Meta:
        model = Profile
        fields = ('nickname', 'avatar')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['email'].initial = self.user.email
        if self.data.get('avatar_uploaded'):
            self.files = self.files or {}
            self.files['avatar'] = self.instance.avatar

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.user.pk).exists():
            raise forms.ValidationError("This email is already in use")
        return email

    def clean_nickname(self):
        nickname = self.cleaned_data.get('nickname')
        if Profile.objects.filter(nickname=nickname).exclude(user=self.user).exists():
            raise forms.ValidationError("This nickname is already in use")
        return nickname

    def save(self, commit=True):
        profile = super().save(commit=False)
        if 'avatar' in self.files:
            profile.avatar = self.files['avatar']
        profile.login = self.cleaned_data['nickname']
        if commit:
            profile.save()
            self.user.email = self.cleaned_data['email']
            self.user.save()
        return profile


class AskForm(forms.Form):
    title = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'How to build a moon park?',
            'id': 'questionTitle'
        }),
        label='Title',
        required=True
    )
    text = forms.CharField(
        max_length=2000,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Really, how? Have no idea about it',
            'id': 'questionText'
        }),
        label='Text',
        required=True
    )
    tags = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'moon, park, puzzle',
            'id': 'questionTags'
        }),
        label='Tags',
        required=False
    )

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) < 2:
            raise forms.ValidationError("Title must be at least 2 characters long")
        return title

    def clean_text(self):
        text = self.cleaned_data.get('text')
        if len(text) < 5:
            raise forms.ValidationError("Question text must be at least 5 characters long")
        return text

    def clean_tags(self):
        tags = self.cleaned_data.get('tags', '')
        tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
        if len(tag_list) > 3:
            raise forms.ValidationError("You can specify no more than 3 tags")
        return tags


class AnswerForm(forms.Form):
    text = forms.CharField(
        max_length=2000,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Enter your answer here.',
            'id': 'answerText'
        }),
        label='Your Answer',
        required=True
    )

    def clean_text(self):
        text = self.cleaned_data.get('text')
        if len(text) < 2:
            raise forms.ValidationError("Answer text must be at least 2 characters long")
        return text
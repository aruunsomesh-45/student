from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from .models import User

class StudentSignUpForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Choose a strong password', 'class': 'form-input'}),
        label='Password'
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm your password', 'class': 'form-input'}),
        label='Confirm Password'
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'academic_tier', 'grade_or_year', 'institution']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Unique username or student ID', 'class': 'form-input'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'First Name', 'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last Name', 'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'placeholder': 'student@school.edu', 'class': 'form-input'}),
            'academic_tier': forms.Select(attrs={'class': 'form-select'}),
            'grade_or_year': forms.TextInput(attrs={'placeholder': 'e.g. 10th Grade / 3rd Year CS', 'class': 'form-input'}),
            'institution': forms.TextInput(attrs={'placeholder': 'School or University name', 'class': 'form-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['academic_tier'].required = True
        self.fields['email'].required = True
        self.fields['first_name'].required = True

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', 'Passwords do not match.')
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.STUDENT
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class TeacherSignUpForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Choose a strong password', 'class': 'form-input'}),
        label='Password'
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm your password', 'class': 'form-input'}),
        label='Confirm Password'
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'institution', 'department_or_subject']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Teacher username / email', 'class': 'form-input'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'First Name', 'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last Name', 'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'placeholder': 'teacher@school.edu', 'class': 'form-input'}),
            'institution': forms.TextInput(attrs={'placeholder': 'School or College name', 'class': 'form-input'}),
            'department_or_subject': forms.TextInput(attrs={'placeholder': 'e.g. Mathematics, Science, Computer Science', 'class': 'form-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['first_name'].required = True

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', 'Passwords do not match.')
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.TEACHER
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Username or Email',
        widget=forms.TextInput(attrs={'placeholder': 'Username or Email', 'class': 'form-input', 'autofocus': True})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Your password', 'class': 'form-input'})
    )

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username is not None and password:
            self.user_cache = authenticate(self.request, username=username.strip(), password=password)
            if self.user_cache is None:
                # If username direct auth fails, look up user by email address
                try:
                    user_match = User.objects.filter(email__iexact=username.strip()).first()
                    if user_match:
                        self.user_cache = authenticate(self.request, username=user_match.username, password=password)
                except Exception:
                    pass

            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data


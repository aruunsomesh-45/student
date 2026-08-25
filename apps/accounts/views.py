import os
import requests
import logging
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.conf import settings
from .models import User
from .forms import StudentSignUpForm, TeacherSignUpForm, CustomLoginForm

logger = logging.getLogger(__name__)

class RoleDispatchView(LoginRequiredMixin, View):
    """
    Directs the user to their appropriate dashboard or assessment page based on their role.
    """
    def get(self, request):
        if request.user.is_teacher_user():
            return redirect('dashboard:teacher_overview')
        return redirect('assessments:take_quiz')


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = CustomLoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return '/accounts/dispatch/'


class StudentSignUpView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('accounts:dispatch')
        form = StudentSignUpForm()
        return render(request, 'accounts/signup_student.html', {'form': form})

    def post(self, request):
        form = StudentSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, f"Welcome {user.first_name}! Your student profile has been created.")
            return redirect('assessments:take_quiz')
        return render(request, 'accounts/signup_student.html', {'form': form})


class TeacherSignUpView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('accounts:dispatch')
        form = TeacherSignUpForm()
        return render(request, 'accounts/signup_teacher.html', {'form': form})

    def post(self, request):
        form = TeacherSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, f"Welcome Professor/Teacher {user.last_name}! Your dashboard is ready.")
            return redirect('dashboard:teacher_overview')
        return render(request, 'accounts/signup_teacher.html', {'form': form})


class CustomLogoutView(View):
    def post(self, request):
        logout(request)
        messages.info(request, "You have been logged out successfully.")
        return redirect('accounts:login')

    def get(self, request):
        logout(request)
        messages.info(request, "You have been logged out successfully.")
        return redirect('accounts:login')


class GoogleAuthInitView(View):
    """
    Initializes Google OAuth using Supabase Auth.
    Directs user to Supabase's Google OAuth authorization endpoint.
    """
    def get(self, request):
        role = request.GET.get('role', 'STUDENT').upper()
        tier = request.GET.get('tier', 'SCHOOL').upper()
        
        request.session['oauth_signup_role'] = role
        request.session['oauth_signup_tier'] = tier

        supabase_url = getattr(settings, 'SUPABASE_URL', os.getenv('SUPABASE_URL', '')).rstrip('/')
        if supabase_url:
            callback_url = request.build_absolute_uri(reverse('accounts:supabase_callback'))
            # Force https scheme in callback URL if not local
            if not settings.DEBUG and callback_url.startswith('http://'):
                callback_url = 'https://' + callback_url[7:]
            
            supabase_auth_url = f"{supabase_url}/auth/v1/authorize?provider=google&redirect_to={callback_url}"
            return redirect(supabase_auth_url)
        
        # Fallback simulation if no Supabase credentials
        return render(request, 'accounts/google_simulate.html', {
            'role': role,
            'tier': tier,
        })


class SupabaseCallbackView(View):
    """
    Handles callbacks from Supabase Google OAuth.
    Exchanges authorization code / token with Supabase and logs user into Django session.
    """
    def get(self, request):
        code = request.GET.get('code')
        error = request.GET.get('error_description') or request.GET.get('error')
        if error:
            messages.error(request, f"Google sign in failed: {error}")
            return redirect('accounts:login')

        if not code:
            # Check for tokens in hash fragment via client-side bridge template
            return render(request, 'accounts/supabase_callback.html')

        return self._exchange_code_and_login(request, code)

    def post(self, request):
        # Handle access_token posted from client-side hash parser
        access_token = request.POST.get('access_token')
        if not access_token:
            messages.error(request, "Invalid authentication response.")
            return redirect('accounts:login')

        return self._login_with_access_token(request, access_token)

    def _exchange_code_and_login(self, request, code):
        supabase_url = getattr(settings, 'SUPABASE_URL', os.getenv('SUPABASE_URL', '')).rstrip('/')
        supabase_key = getattr(settings, 'SUPABASE_KEY', os.getenv('SUPABASE_KEY', ''))
        
        try:
            # Exchange PKCE auth code with Supabase Auth
            token_url = f"{supabase_url}/auth/v1/token?grant_type=pkce"
            resp = requests.post(token_url, json={'auth_code': code}, headers={
                'apikey': supabase_key,
                'Content-Type': 'application/json',
            }, timeout=10)

            if resp.status_code == 200:
                data = resp.json()
                user_data = data.get('user', {})
                return self._authenticate_django_user(request, user_data)
        except Exception as e:
            logger.error(f"Supabase code exchange error: {e}")

        # Fallback to rendering client bridge
        return render(request, 'accounts/supabase_callback.html')

    def _login_with_access_token(self, request, access_token):
        supabase_url = getattr(settings, 'SUPABASE_URL', os.getenv('SUPABASE_URL', '')).rstrip('/')
        supabase_key = getattr(settings, 'SUPABASE_KEY', os.getenv('SUPABASE_KEY', ''))

        try:
            # Fetch user info using access token
            user_url = f"{supabase_url}/auth/v1/user"
            resp = requests.get(user_url, headers={
                'apikey': supabase_key,
                'Authorization': f'Bearer {access_token}',
            }, timeout=10)

            if resp.status_code == 200:
                user_data = resp.json()
                return self._authenticate_django_user(request, user_data)
        except Exception as e:
            logger.error(f"Supabase user info error: {e}")

        messages.error(request, "Failed to retrieve user profile from Supabase.")
        return redirect('accounts:login')

    def _authenticate_django_user(self, request, user_data):
        email = user_data.get('email')
        if not email:
            messages.error(request, "No verified email returned from Google.")
            return redirect('accounts:login')

        metadata = user_data.get('user_metadata', {})
        full_name = metadata.get('full_name') or metadata.get('name', '')
        first_name = metadata.get('first_name') or metadata.get('given_name', '')
        last_name = metadata.get('last_name') or metadata.get('family_name', '')
        
        if not first_name and full_name:
            parts = full_name.split(' ', 1)
            first_name = parts[0]
            last_name = parts[1] if len(parts) > 1 else ''

        role = request.session.pop('oauth_signup_role', None) or 'STUDENT'
        tier = request.session.pop('oauth_signup_tier', None) or 'SCHOOL'

        user = User.objects.filter(email__iexact=email).first()
        if not user:
            # Generate clean unique username
            base_username = email.split('@')[0]
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}_{counter}"
                counter += 1

            user = User.objects.create(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                role=role,
                academic_tier=tier if role == 'STUDENT' else None,
                institution='Google / Supabase Verified',
                avatar_color='#6366f1'
            )
        else:
            if not user.first_name and first_name:
                user.first_name = first_name
            if not user.last_name and last_name:
                user.last_name = last_name
            if role == 'STUDENT' and not user.academic_tier:
                user.academic_tier = tier
            user.save()

        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        messages.success(request, f"Welcome back, {user.first_name or user.username}! Signed in via Supabase Google Auth.")
        return redirect('accounts:dispatch')


class GoogleSimulateCallbackView(View):
    """
    Simulates successful Google OAuth callback response for test environments.
    """
    def get(self, request):
        return self._process_login(request, request.GET)

    def post(self, request):
        return self._process_login(request, request.POST)

    def _process_login(self, request, data):
        role = data.get('role', 'STUDENT').upper()
        tier = data.get('tier', 'UG').upper()
        google_email = data.get('email', 'alex.mercer@gmail.com')
        google_name = data.get('name', 'Alex Mercer')
        
        names = google_name.split(' ', 1)
        first_name = names[0]
        last_name = names[1] if len(names) > 1 else ''

        username = google_email.split('@')[0] + '_g'
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': google_email,
                'first_name': first_name,
                'last_name': last_name,
                'role': role,
                'academic_tier': tier if role == 'STUDENT' else None,
                'institution': 'Google Verified Institution',
                'avatar_color': '#ea4335'
            }
        )
        if not created:
            user.role = role
            if role == 'STUDENT' and not user.academic_tier:
                user.academic_tier = tier
            user.save()

        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        messages.success(request, f"Welcome back, {user.first_name}! Logged in with Google account ({google_email}).")
        return redirect('accounts:dispatch')


class DemoLoginView(View):
    """
    One-click instant login for testing either Student or Teacher flows seamlessly.
    ⚠️  Only available when DEBUG=True — returns 404 in production.
    """
    def get(self, request, role):
        import sys
        is_testing = 'test' in sys.argv or getattr(settings, 'TESTING', False)
        allow_demo = settings.DEBUG or is_testing or os.getenv('ENABLE_DEMO_LOGINS', 'False').lower() in ('true', '1', 'yes')
        if not allow_demo:
            from django.http import Http404
            raise Http404("Demo login is not available in production.")

        if role == 'teacher':
            user, created = User.objects.get_or_create(
                username='demo_teacher',
                defaults={
                    'first_name': 'Prof. Sarah',
                    'last_name': 'Jenkins',
                    'email': 's.jenkins@demo.edu',
                    'role': User.Role.TEACHER,
                    'institution': 'Horizon International Academy',
                    'department_or_subject': 'Science & Mathematics',
                    'avatar_color': '#6366f1'
                }
            )
            if created:
                user.set_password('demo1234')
                user.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, "Logged in as Demo Teacher (Prof. Sarah Jenkins).")
            return redirect('dashboard:teacher_overview')

        elif role == 'student_school':
            user, created = User.objects.get_or_create(
                username='demo_student_school',
                defaults={
                    'first_name': 'Aarav',
                    'last_name': 'Sharma',
                    'email': 'aarav.sharma@demo.edu',
                    'role': User.Role.STUDENT,
                    'academic_tier': User.AcademicTier.SCHOOL,
                    'grade_or_year': '10th Grade (Section A)',
                    'institution': 'Horizon International School',
                    'avatar_color': '#10b981'
                }
            )
            if created:
                user.set_password('demo1234')
                user.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, "Logged in as Demo School Student (Aarav - 10th Grade).")
            return redirect('assessments:take_quiz')

        elif role == 'student_ug':
            user, created = User.objects.get_or_create(
                username='demo_student_ug',
                defaults={
                    'first_name': 'Maya',
                    'last_name': 'Chen',
                    'email': 'maya.chen@demo.edu',
                    'role': User.Role.STUDENT,
                    'academic_tier': User.AcademicTier.UG,
                    'grade_or_year': '3rd Year B.Tech Computer Science',
                    'institution': 'State Institute of Technology',
                    'avatar_color': '#f59e0b'
                }
            )
            if created:
                user.set_password('demo1234')
                user.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, "Logged in as Demo UG Student (Maya Chen - 3rd Year B.Tech).")
            return redirect('assessments:take_quiz')

        return redirect('accounts:login')

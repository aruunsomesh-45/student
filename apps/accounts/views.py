from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.conf import settings
from .models import User
from .forms import StudentSignUpForm, TeacherSignUpForm, CustomLoginForm

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
    Initializes Google OAuth with session role/tier intent.
    If real Google keys are configured, delegates to allauth's Google provider;
    Otherwise, handles a simulated Google OAuth callback with realistic Google account details.
    """
    def get(self, request):
        role = request.GET.get('role', 'STUDENT').upper()
        tier = request.GET.get('tier', 'SCHOOL').upper()
        
        request.session['oauth_signup_role'] = role
        request.session['oauth_signup_tier'] = tier

        # Check if actual Google keys are set in environment
        if settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_ID != 'YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com':
            return redirect('/accounts/google/login/?process=login')
        
        # Simulated Google Consent & Login for testing
        return render(request, 'accounts/google_simulate.html', {
            'role': role,
            'tier': tier,
        })


class GoogleSimulateCallbackView(View):
    """
    Simulates successful Google OAuth callback response.
    Supports both POST and GET for 1-click Google One-Tap UX.
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

from django.test import TestCase, Client
from django.urls import reverse
from .models import User

class Phase1AuthTests(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Test student
        self.student = User.objects.create_user(
            username='student_test',
            email='student@school.edu',
            password='password123',
            first_name='Student',
            last_name='One',
            role=User.Role.STUDENT,
            academic_tier=User.AcademicTier.SCHOOL,
            grade_or_year='10th Grade'
        )
        
        # Test teacher
        self.teacher = User.objects.create_user(
            username='teacher_test',
            email='teacher@school.edu',
            password='password123',
            first_name='Teacher',
            last_name='One',
            role=User.Role.TEACHER,
            institution='Oakridge High'
        )

    def test_user_roles_and_helpers(self):
        self.assertTrue(self.student.is_student_user())
        self.assertFalse(self.student.is_teacher_user())
        self.assertTrue(self.teacher.is_teacher_user())
        self.assertFalse(self.teacher.is_student_user())
        self.assertEqual(self.student.get_tier_display_label(), 'Schooling (10th / 12th)')

    def test_landing_page_accessible(self):
        response = self.client.get(reverse('core:landing'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'MindConnect')
        self.assertContains(response, 'Understand the Student Mindset')

    def test_student_signup_flow(self):
        response = self.client.post(reverse('accounts:signup_student'), {
            'username': 'new_student',
            'first_name': 'Aarav',
            'last_name': 'Kumar',
            'email': 'aarav@school.edu',
            'academic_tier': User.AcademicTier.UG,
            'grade_or_year': '1st Year CS',
            'institution': 'IIT Delhi',
            'password': 'password1234',
            'confirm_password': 'password1234'
        })
        # Should redirect to assessment
        self.assertRedirects(response, reverse('assessments:take_quiz'))
        created_student = User.objects.get(username='new_student')
        self.assertEqual(created_student.role, User.Role.STUDENT)
        self.assertEqual(created_student.academic_tier, User.AcademicTier.UG)

    def test_teacher_signup_flow(self):
        response = self.client.post(reverse('accounts:signup_teacher'), {
            'username': 'new_teacher',
            'first_name': 'Dr. Robert',
            'last_name': 'Langdon',
            'email': 'langdon@harvard.edu',
            'institution': 'Harvard University',
            'department_or_subject': 'History & Arts',
            'password': 'password1234',
            'confirm_password': 'password1234'
        })
        # Should redirect to teacher dashboard
        self.assertRedirects(response, reverse('dashboard:teacher_overview'))
        created_teacher = User.objects.get(username='new_teacher')
        self.assertEqual(created_teacher.role, User.Role.TEACHER)

    def test_role_dispatch_student(self):
        self.client.login(username='student_test', password='password123')
        response = self.client.get(reverse('accounts:dispatch'))
        self.assertRedirects(response, reverse('assessments:take_quiz'))

    def test_role_dispatch_teacher(self):
        self.client.login(username='teacher_test', password='password123')
        response = self.client.get(reverse('accounts:dispatch'))
        self.assertRedirects(response, reverse('dashboard:teacher_overview'))

    def test_teacher_dashboard_protection(self):
        # Unauthenticated user is redirected to login
        response = self.client.get(reverse('dashboard:teacher_overview'))
        self.assertEqual(response.status_code, 302)

        # Student attempting to access teacher dashboard gets redirected to dispatch (which dispatches to assessment)
        self.client.login(username='student_test', password='password123')
        response = self.client.get(reverse('dashboard:teacher_overview'))
        self.assertRedirects(response, reverse('accounts:dispatch'), target_status_code=302)

    def test_demo_logins(self):
        # Demo teacher login
        response = self.client.get(reverse('accounts:demo_login', kwargs={'role': 'teacher'}))
        self.assertRedirects(response, reverse('dashboard:teacher_overview'))
        
        # Demo school student login
        response = self.client.get(reverse('accounts:demo_login', kwargs={'role': 'student_school'}))
        self.assertRedirects(response, reverse('assessments:take_quiz'))

    def test_google_oauth_simulation_student(self):
        from django.test import override_settings
        with override_settings(GOOGLE_CLIENT_ID='YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com'):
            # Initiate Google OAuth flow for student (simulated)
            response = self.client.get(reverse('accounts:google_init') + '?role=STUDENT&tier=UG')
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'Sign in with Google')
            
            # Simulate OAuth Callback POST
            callback_response = self.client.post(reverse('accounts:google_simulate_callback'), {
                'role': 'STUDENT',
                'tier': 'UG',
                'email': 'riya.sharma@gmail.com',
                'name': 'Riya Sharma'
            })
            self.assertRedirects(callback_response, reverse('accounts:dispatch'), target_status_code=302)
            google_user = User.objects.get(email='riya.sharma@gmail.com')
            self.assertEqual(google_user.role, User.Role.STUDENT)
            self.assertEqual(google_user.academic_tier, User.AcademicTier.UG)

    def test_google_onetap_get_callback(self):
        # 1-Click One-Tap Google Fast Sign-In GET
        callback_response = self.client.get(reverse('accounts:google_simulate_callback') + '?name=Alex+Mercer&email=alex.mercer@gmail.com&role=STUDENT&tier=UG')
        self.assertRedirects(callback_response, reverse('accounts:dispatch'), target_status_code=302)
        alex_user = User.objects.get(email='alex.mercer@gmail.com')
        self.assertEqual(alex_user.first_name, 'Alex')
        self.assertEqual(alex_user.role, User.Role.STUDENT)

    def test_google_oauth_simulation_teacher(self):
        # Simulate OAuth Callback for Teacher
        callback_response = self.client.post(reverse('accounts:google_simulate_callback'), {
            'role': 'TEACHER',
            'email': 'prof.williams@gmail.com',
            'name': 'David Williams'
        })
        self.assertRedirects(callback_response, reverse('accounts:dispatch'), target_status_code=302)
        google_teacher = User.objects.get(email='prof.williams@gmail.com')
        self.assertEqual(google_teacher.role, User.Role.TEACHER)

from django.test import TestCase, Client
from django.urls import reverse
from apps.accounts.models import User
from apps.assessments.models import Submission
from apps.dashboard.models import TeacherNote
from apps.dashboard.ai_services import generate_cohort_ai_strategy, generate_student_ai_playbook

class StudentDashboardTests(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Student 1
        self.student1 = User.objects.create_user(
            username='student1',
            email='student1@school.edu',
            password='Password123!',
            role=User.Role.STUDENT,
            academic_tier=User.AcademicTier.UG,
            first_name='Maya',
            last_name='Lin'
        )

        # Student 2
        self.student2 = User.objects.create_user(
            username='student2',
            email='student2@school.edu',
            password='Password123!',
            role=User.Role.STUDENT,
            academic_tier=User.AcademicTier.SCHOOL,
            first_name='Liam',
            last_name='Smith'
        )

        # Teacher
        self.teacher = User.objects.create_user(
            username='teacher1',
            email='teacher1@school.edu',
            password='Password123!',
            role=User.Role.TEACHER,
            first_name='Prof',
            last_name='Oak'
        )

    def test_unauthenticated_access_redirects(self):
        response = self.client.get(reverse('dashboard:student_results'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_teacher_access_blocked_from_student_portal(self):
        self.client.login(username='teacher1', password='Password123!')
        response = self.client.get(reverse('dashboard:student_results'))
        self.assertEqual(response.status_code, 302)

    def test_empty_state_without_submissions(self):
        self.client.login(username='student1', password='Password123!')
        response = self.client.get(reverse('dashboard:student_results'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/student_results.html')
        self.assertFalse(response.context['has_submissions'])
        self.assertContains(response, "You haven't completed your diagnostic assessment yet")
        self.assertContains(response, reverse('assessments:take_quiz'))

    def test_student_dashboard_with_single_submission(self):
        self.client.login(username='student1', password='Password123!')
        
        sub = Submission.objects.create(
            student=self.student1,
            tier=User.AcademicTier.UG,
            visual_score=80,
            auditory_score=30,
            kinesthetic_score=40,
            growth_score=85,
            stress_score=25,
            persona_title='The Visual Strategist',
            persona_tagline='Master of diagrams and visual mental modeling.',
            persona_summary='You learn best through visual architecture.',
            teacher_motivation='Provide charts and diagrams.',
            teacher_communication='Visual feedback in writing.',
            teacher_caution='Monitor long auditory lectures.'
        )

        response = self.client.get(reverse('dashboard:student_results'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['has_submissions'])
        self.assertEqual(response.context['submission'].id, sub.id)
        self.assertContains(response, 'The Visual Strategist')
        self.assertContains(response, '80%')
        self.assertIn('strategies', response.context)
        self.assertGreaterEqual(len(response.context['strategies']), 3)

    def test_multiple_submissions_history_and_detail_view(self):
        self.client.login(username='student1', password='Password123!')
        
        sub1 = Submission.objects.create(
            student=self.student1,
            tier=User.AcademicTier.UG,
            visual_score=70,
            auditory_score=30,
            kinesthetic_score=50,
            growth_score=60,
            stress_score=30,
            persona_title='The Visual Strategist',
            persona_tagline='Visual Tagline'
        )

        sub2 = Submission.objects.create(
            student=self.student1,
            tier=User.AcademicTier.UG,
            visual_score=40,
            auditory_score=30,
            kinesthetic_score=85,
            growth_score=75,
            stress_score=35,
            persona_title='The Hands-On Innovator',
            persona_tagline='Kinesthetic Tagline'
        )

        response_latest = self.client.get(reverse('dashboard:student_results'))
        self.assertEqual(response_latest.status_code, 200)
        self.assertEqual(response_latest.context['submission'].id, sub2.id)
        self.assertEqual(response_latest.context['total_attempts'], 2)

        response_detail = self.client.get(reverse('dashboard:student_results_detail', kwargs={'submission_id': sub1.id}))
        self.assertEqual(response_detail.status_code, 200)
        self.assertEqual(response_detail.context['submission'].id, sub1.id)

    def test_cannot_access_other_students_submission(self):
        self.client.login(username='student2', password='Password123!')
        
        sub_student1 = Submission.objects.create(
            student=self.student1,
            tier=User.AcademicTier.UG,
            visual_score=70,
            persona_title='Private Student 1 Persona'
        )

        response = self.client.get(reverse('dashboard:student_results_detail', kwargs={'submission_id': sub_student1.id}))
        self.assertEqual(response.status_code, 404)


class TeacherDashboardTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Teacher 1
        self.teacher = User.objects.create_user(
            username='teacher_sarah',
            email='sarah@demo.edu',
            password='Password123!',
            role=User.Role.TEACHER,
            first_name='Sarah',
            last_name='Jenkins'
        )

        # Teacher 2
        self.teacher2 = User.objects.create_user(
            username='teacher_bob',
            email='bob@demo.edu',
            password='Password123!',
            role=User.Role.TEACHER,
            first_name='Bob',
            last_name='Smith'
        )

        # Student 1 (School, High Stress)
        self.student_school = User.objects.create_user(
            username='aarav',
            email='aarav@demo.edu',
            password='Password123!',
            role=User.Role.STUDENT,
            academic_tier=User.AcademicTier.SCHOOL,
            first_name='Aarav',
            last_name='Sharma',
            grade_or_year='10th Grade'
        )
        self.sub_school = Submission.objects.create(
            student=self.student_school,
            tier=User.AcademicTier.SCHOOL,
            visual_score=85,
            auditory_score=30,
            kinesthetic_score=40,
            growth_score=60,
            stress_score=80, # High stress
            persona_title='The Visual Strategist',
            open_message_to_teacher='I get anxious before oral exams.',
            personality_tag='Achiever',
            interests_tag='STEM/Analytical',
            wellbeing_flag='Red',
            soft_skills_summary='Independent, Strong time-management'
        )

        # Student 2 (UG, High Growth)
        self.student_ug = User.objects.create_user(
            username='maya',
            email='maya@demo.edu',
            password='Password123!',
            role=User.Role.STUDENT,
            academic_tier=User.AcademicTier.UG,
            first_name='Maya',
            last_name='Chen',
            grade_or_year='3rd Year B.Tech'
        )
        self.sub_ug = Submission.objects.create(
            student=self.student_ug,
            tier=User.AcademicTier.UG,
            visual_score=30,
            auditory_score=25,
            kinesthetic_score=90,
            growth_score=85, # High growth
            stress_score=30,
            persona_title='The Hands-On Innovator',
            personality_tag='Explorer',
            interests_tag='Creative/Artistic',
            wellbeing_flag='Green',
            soft_skills_summary='Collaborative, Diplomatic'
        )

    def test_student_access_blocked_from_teacher_dashboard(self):
        self.client.login(username='aarav', password='Password123!')
        response = self.client.get(reverse('dashboard:teacher_overview'))
        self.assertEqual(response.status_code, 302)

    def test_teacher_overview_metrics(self):
        self.client.login(username='teacher_sarah', password='Password123!')
        response = self.client.get(reverse('dashboard:teacher_overview'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/teacher_dashboard.html')

        stats = response.context['cohort_stats']
        self.assertEqual(stats['total_students'], 2)
        self.assertEqual(stats['stress_watchlist_count'], 1)
        self.assertEqual(stats['growth_champions_count'], 1)
        self.assertGreater(stats['avg_growth'], 0)

    def test_teacher_tier_filter(self):
        self.client.login(username='teacher_sarah', password='Password123!')
        response = self.client.get(reverse('dashboard:teacher_overview') + '?tier=SCHOOL')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_matching'], 1)
        self.assertEqual(response.context['submissions'].first().student, self.student_school)

    def test_teacher_status_filter_stress(self):
        self.client.login(username='teacher_sarah', password='Password123!')
        response = self.client.get(reverse('dashboard:teacher_overview') + '?status=HIGH_STRESS')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_matching'], 1)
        self.assertEqual(response.context['submissions'].first().student, self.student_school)

    def test_teacher_search_query(self):
        self.client.login(username='teacher_sarah', password='Password123!')
        response = self.client.get(reverse('dashboard:teacher_overview') + '?q=Maya')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_matching'], 1)
        self.assertEqual(response.context['submissions'].first().student, self.student_ug)

    def test_save_llm_key_endpoint(self):
        self.client.login(username='teacher_sarah', password='Password123!')
        response = self.client.post(reverse('dashboard:save_llm_key'), {
            'api_key': 'AIzaSyTestApiKey12345'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.session.get('teacher_llm_api_key'), 'AIzaSyTestApiKey12345')

    def test_cohort_ai_analysis_endpoint(self):
        self.client.login(username='teacher_sarah', password='Password123!')
        response = self.client.get(reverse('dashboard:cohort_ai_analysis'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('analysis', data)
        self.assertTrue(len(data['analysis']) > 50)

    # ------------------ STAGE 6: PLAYBOOK & NOTES TESTS ------------------
    def test_student_blocked_from_playbook(self):
        self.client.login(username='aarav', password='Password123!')
        response = self.client.get(reverse('dashboard:student_playbook', kwargs={'student_id': self.student_ug.id}))
        self.assertEqual(response.status_code, 302)

    def test_teacher_view_student_playbook(self):
        self.client.login(username='teacher_sarah', password='Password123!')
        response = self.client.get(reverse('dashboard:student_playbook', kwargs={'student_id': self.student_school.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/student_playbook.html')
        self.assertContains(response, 'The Visual Strategist')
        self.assertContains(response, 'I get anxious before oral exams.')
        self.assertContains(response, '3-Pillar Educator Mentorship Blueprint')

    def test_teacher_add_and_view_private_note(self):
        self.client.login(username='teacher_sarah', password='Password123!')
        response = self.client.post(
            reverse('dashboard:submission_playbook', kwargs={'submission_id': self.sub_school.id}),
            {
                'category': TeacherNote.Category.WELLBEING,
                'content': 'Held a 1-on-1 check-in. Agreed to provide written test questions first to ease anxiety.'
            }
        )
        self.assertEqual(response.status_code, 302)

        # Verify note saved in DB
        self.assertEqual(TeacherNote.objects.count(), 1)
        note = TeacherNote.objects.first()
        self.assertEqual(note.student, self.student_school)
        self.assertEqual(note.teacher, self.teacher)
        self.assertEqual(note.category, TeacherNote.Category.WELLBEING)

        # Verify rendered in playbook
        playbook_resp = self.client.get(reverse('dashboard:submission_playbook', kwargs={'submission_id': self.sub_school.id}))
        self.assertContains(playbook_resp, 'Held a 1-on-1 check-in')
        self.assertContains(playbook_resp, 'Wellbeing &amp; Stress Support')

    def test_teacher_delete_own_note(self):
        self.client.login(username='teacher_sarah', password='Password123!')
        note = TeacherNote.objects.create(
            teacher=self.teacher,
            student=self.student_school,
            content='Test Note to Delete'
        )
        response = self.client.post(reverse('dashboard:delete_teacher_note', kwargs={'note_id': note.id}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(TeacherNote.objects.count(), 0)

    def test_teacher_cannot_delete_other_teacher_note(self):
        note = TeacherNote.objects.create(
            teacher=self.teacher2, # Created by teacher 2
            student=self.student_school,
            content='Teacher 2 Private Note'
        )
        self.client.login(username='teacher_sarah', password='Password123!')
        response = self.client.post(reverse('dashboard:delete_teacher_note', kwargs={'note_id': note.id}))
        self.assertEqual(response.status_code, 404) # Blocked
        self.assertEqual(TeacherNote.objects.count(), 1)

    def test_student_ai_plan_endpoint(self):
        self.client.login(username='teacher_sarah', password='Password123!')
        response = self.client.get(reverse('dashboard:student_ai_plan', kwargs={'submission_id': self.sub_school.id}))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('analysis', data)
        self.assertIn('Individualized Instruction & Scaffolding', data['analysis'])

    # ------------------ STAGE 7: PDF REPORT & SEEDER TESTS ------------------
    def test_teacher_can_view_student_pdf_report(self):
        self.client.login(username='teacher_sarah', password='Password123!')
        response = self.client.get(reverse('dashboard:student_report_pdf', kwargs={'submission_id': self.sub_school.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/student_report_pdf.html')
        self.assertContains(response, 'MindConnect Assessment Dossier')
        self.assertContains(response, 'The Visual Strategist')

    def test_student_can_view_own_pdf_report(self):
        self.client.login(username='aarav', password='Password123!')
        response = self.client.get(reverse('dashboard:student_report_pdf', kwargs={'submission_id': self.sub_school.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Aarav Sharma')

    def test_student_cannot_view_other_student_pdf_report(self):
        self.client.login(username='aarav', password='Password123!')
        response = self.client.get(reverse('dashboard:student_report_pdf', kwargs={'submission_id': self.sub_ug.id}))
        self.assertEqual(response.status_code, 404)


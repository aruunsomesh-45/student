from django.test import TestCase, Client
from django.urls import reverse
from django.core.management import call_command
from apps.accounts.models import User
from apps.assessments.models import Question, Choice, Submission, SubmissionAnswer
from apps.assessments.services import (
    compute_psychometric_scores,
    determine_persona,
    generate_student_strategies,
    generate_teacher_playbook,
    calculate_and_save_submission
)

class MockChoice:
    def __init__(self, visual=0, auditory=0, kinesthetic=0, growth=0, stress=0):
        self.visual_weight = visual
        self.auditory_weight = auditory
        self.kinesthetic_weight = kinesthetic
        self.growth_weight = growth
        self.stress_weight = stress


class ScoringEngineUnitTests(TestCase):
    def test_compute_psychometric_scores_empty(self):
        scores = compute_psychometric_scores([])
        self.assertEqual(scores['visual_score'], 0)
        self.assertEqual(scores['auditory_score'], 0)
        self.assertEqual(scores['kinesthetic_score'], 0)
        self.assertEqual(scores['growth_score'], 0)
        self.assertEqual(scores['stress_score'], 0)

    def test_compute_psychometric_scores_max_and_normalization(self):
        # 4 choices with max weight (5) in visual and growth
        choices = [
            MockChoice(visual=5, auditory=1, kinesthetic=2, growth=5, stress=1),
            MockChoice(visual=5, auditory=0, kinesthetic=1, growth=5, stress=0),
            MockChoice(visual=5, auditory=2, kinesthetic=2, growth=5, stress=2),
            MockChoice(visual=5, auditory=1, kinesthetic=1, growth=5, stress=1),
        ]
        # max possible weight = 4 * 5 = 20
        # visual sum = 20 -> 100%
        # growth sum = 20 -> 100%
        # auditory sum = 4 -> 20%
        # kinesthetic sum = 6 -> 30%
        # stress sum = 4 -> 20%
        scores = compute_psychometric_scores(choices)
        self.assertEqual(scores['visual_score'], 100)
        self.assertEqual(scores['growth_score'], 100)
        self.assertEqual(scores['auditory_score'], 20)
        self.assertEqual(scores['kinesthetic_score'], 30)
        self.assertEqual(scores['stress_score'], 20)

    def test_determine_persona_types(self):
        # Test Visual Strategist
        v_persona = determine_persona({'visual_score': 85, 'auditory_score': 40, 'kinesthetic_score': 50, 'growth_score': 50, 'stress_score': 50})
        self.assertEqual(v_persona['title'], 'The Visual Strategist')

        # Test Hands-On Innovator
        k_persona = determine_persona({'visual_score': 40, 'auditory_score': 30, 'kinesthetic_score': 90, 'growth_score': 50, 'stress_score': 50})
        self.assertEqual(k_persona['title'], 'The Hands-On Innovator')

        # Test Socratic Collaborator
        a_persona = determine_persona({'visual_score': 30, 'auditory_score': 85, 'kinesthetic_score': 40, 'growth_score': 50, 'stress_score': 50})
        self.assertEqual(a_persona['title'], 'The Socratic Collaborator')

        # Test Resilient Deep-Thinker
        r_persona = determine_persona({'visual_score': 65, 'auditory_score': 60, 'kinesthetic_score': 65, 'growth_score': 85, 'stress_score': 25})
        self.assertEqual(r_persona['title'], 'The Resilient Deep-Thinker')

        # Test Analytical Synthesizer fallback
        s_persona = determine_persona({'visual_score': 50, 'auditory_score': 50, 'kinesthetic_score': 50, 'growth_score': 50, 'stress_score': 50})
        self.assertEqual(s_persona['title'], 'The Analytical Synthesizer')

    def test_generate_student_strategies_by_tier(self):
        scores = {'visual_score': 80, 'auditory_score': 40, 'kinesthetic_score': 30, 'growth_score': 60, 'stress_score': 70}
        persona = {'title': 'The Visual Strategist'}

        # School Tier
        school_strats = generate_student_strategies(scores, persona, User.AcademicTier.SCHOOL)
        self.assertEqual(len(school_strats), 3)
        self.assertTrue(any('Mind Map' in s['title'] for s in school_strats))
        self.assertTrue(any('Pomodoro' in s['title'] for s in school_strats))

        # UG Tier
        ug_strats = generate_student_strategies(scores, persona, User.AcademicTier.UG)
        self.assertEqual(len(ug_strats), 3)
        self.assertTrue(any('Architecture' in s['title'] for s in ug_strats))
        self.assertTrue(any('Agile' in s['title'] for s in ug_strats))

        # PG Tier
        pg_strats = generate_student_strategies(scores, persona, User.AcademicTier.PG)
        self.assertEqual(len(pg_strats), 3)
        self.assertTrue(any('Citation' in s['title'] for s in pg_strats))
        self.assertTrue(any('Deep-Work' in s['title'] for s in pg_strats))

    def test_generate_teacher_playbook_and_stress_alert(self):
        low_stress_scores = {'visual_score': 50, 'auditory_score': 50, 'kinesthetic_score': 50, 'growth_score': 80, 'stress_score': 20}
        playbook_low = generate_teacher_playbook(low_stress_scores, {'base_motivation': 'Motivate.', 'base_comm': 'Communicate.', 'base_caution': 'Caution.'})
        self.assertFalse(playbook_low['is_stress_alert'])
        self.assertIn('composure', playbook_low['caution'].lower())

        high_stress_scores = {'visual_score': 50, 'auditory_score': 50, 'kinesthetic_score': 50, 'growth_score': 40, 'stress_score': 75}
        playbook_high = generate_teacher_playbook(high_stress_scores, {'base_motivation': 'Motivate.', 'base_comm': 'Communicate.', 'base_caution': 'Caution.'})
        self.assertTrue(playbook_high['is_stress_alert'])
        self.assertIn('high stress watchlist', playbook_high['caution'].lower())


class AssessmentAppIntegrationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.student = User.objects.create_user(
            username='student_test',
            email='student@school.edu',
            password='Password123!',
            role=User.Role.STUDENT,
            academic_tier=User.AcademicTier.UG,
            first_name='Alex',
            last_name='Rivera'
        )

    def test_full_submission_scoring_flow(self):
        call_command('seed_questions')
        self.client.login(username='student_test', password='Password123!')

        ug_questions = Question.objects.filter(tier=User.AcademicTier.UG)
        post_data = {'tier': User.AcademicTier.UG}
        for q in ug_questions:
            # Select first choice
            choice = q.choices.first()
            post_data[f'question_{q.id}'] = str(choice.id)

        submission = calculate_and_save_submission(self.student, post_data, tier=User.AcademicTier.UG)

        self.assertIsNotNone(submission.id)
        self.assertEqual(submission.student, self.student)
        self.assertEqual(submission.tier, User.AcademicTier.UG)
        self.assertIn(submission.dominant_modality, ['Visual', 'Auditory', 'Kinesthetic'])
        self.assertTrue(len(submission.persona_title) > 0)
        self.assertTrue(len(submission.teacher_motivation) > 0)
        self.assertTrue(len(submission.teacher_communication) > 0)
        self.assertTrue(len(submission.teacher_caution) > 0)

        # Verify results view renders successfully with strategies
        response = self.client.get(reverse('assessments:quiz_success', kwargs={'submission_id': submission.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'assessments/quiz_completed.html')
        self.assertContains(response, submission.persona_title)
        self.assertIn('strategies', response.context)
        self.assertGreaterEqual(len(response.context['strategies']), 3)

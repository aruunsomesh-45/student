from django.core.management.base import BaseCommand
from django.core.management import call_command
from apps.accounts.models import User
from apps.assessments.models import Question, Choice, Submission, SubmissionAnswer
from apps.dashboard.models import TeacherNote
from apps.assessments.services import compute_psychometric_scores, determine_persona, generate_teacher_playbook
import random

class Command(BaseCommand):
    help = 'Seeds 1 demo teacher, 25 realistic students across School, UG, and PG tiers, and test submissions.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Starting MindConnect Demo Data Seeder...'))

        # Ensure question bank is seeded
        if Question.objects.count() == 0:
            self.stdout.write('Question bank empty. Running seed_questions...')
            call_command('seed_questions')

        # 1. Seed / Update Demo Teacher
        teacher, created = User.objects.get_or_create(
            email='teacher@school.edu',
            defaults={
                'username': 'dr_sarah',
                'first_name': 'Dr. Sarah',
                'last_name': 'Jenkins',
                'role': User.Role.TEACHER,
                'institution': 'MindConnect Academic Institute',
                'department_or_subject': 'Cognitive Pedagogy & Engineering',
                'avatar_color': '#6366f1'
            }
        )
        teacher.set_password('Password123!')
        teacher.save()
        self.stdout.write(self.style.SUCCESS(f"Teacher ready: {teacher.email} / Password123!"))

        # 2. 25 Realistic Students Dataset Definition
        students_roster = [
            # --- SCHOOL TIER (Grade 8 to 12) - 8 Students ---
            {
                'username': 'aarav_sharma', 'email': 'aarav.s@school.edu',
                'first_name': 'Aarav', 'last_name': 'Sharma',
                'tier': User.AcademicTier.SCHOOL, 'grade': '10th Grade (CBSE)',
                'institution': 'Delhi Public School', 'color': '#3b82f6',
                'v_bias': 5, 'k_bias': 2, 'a_bias': 2, 'g_bias': 4, 's_bias': 5, # High Stress
                'personality': 'Achiever', 'interests': 'STEM/Analytical', 'wellbeing': 'Red',
                'soft_skills': 'Independent/Reliable, Strong time-management, Diplomatic',
                'msg': 'I get nervous during oral viva examinations and sudden pop quizzes. Having written guides helps me a lot.'
            },
            {
                'username': 'riya_patel', 'email': 'riya.p@school.edu',
                'first_name': 'Riya', 'last_name': 'Patel',
                'tier': User.AcademicTier.SCHOOL, 'grade': '12th Grade (Science)',
                'institution': 'National Public School', 'color': '#10b981',
                'v_bias': 2, 'k_bias': 5, 'a_bias': 2, 'g_bias': 5, 's_bias': 1,
                'personality': 'Explorer', 'interests': 'STEM/Analytical', 'wellbeing': 'Green',
                'soft_skills': 'Idea-generator, Strong time-management, Assertive',
                'msg': 'I love physics laboratory sessions and building circuit kits with my peers.'
            },
            {
                'username': 'kabir_verma', 'email': 'kabir.v@school.edu',
                'first_name': 'Kabir', 'last_name': 'Verma',
                'tier': User.AcademicTier.SCHOOL, 'grade': '9th Grade',
                'institution': 'St. Xavier High School', 'color': '#f59e0b',
                'v_bias': 1, 'k_bias': 2, 'a_bias': 5, 'g_bias': 3, 's_bias': 3,
                'personality': 'Collaborator', 'interests': 'People/Social', 'wellbeing': 'Amber',
                'soft_skills': 'Collaborative, Needs pacing support, Diplomatic',
                'msg': 'I remember lessons best when we do group debates and open discussions in class.'
            },
            {
                'username': 'ananya_sen', 'email': 'ananya.s@school.edu',
                'first_name': 'Ananya', 'last_name': 'Sen',
                'tier': User.AcademicTier.SCHOOL, 'grade': '11th Grade (Humanities)',
                'institution': 'Modern High School', 'color': '#8b5cf6',
                'v_bias': 4, 'k_bias': 2, 'a_bias': 4, 'g_bias': 4, 's_bias': 2,
                'personality': 'Analyst', 'interests': 'Creative/Artistic', 'wellbeing': 'Green',
                'soft_skills': 'Collaborative, Moderate time-management, Assertive',
                'msg': 'I enjoy writing detailed essays and analyzing historical cause-and-effect timelines.'
            },
            {
                'username': 'rohan_gupta', 'email': 'rohan.g@school.edu',
                'first_name': 'Rohan', 'last_name': 'Gupta',
                'tier': User.AcademicTier.SCHOOL, 'grade': '10th Grade',
                'institution': 'Ryan International School', 'color': '#06b6d4',
                'v_bias': 4, 'k_bias': 4, 'a_bias': 1, 'g_bias': 4, 's_bias': 2,
                'personality': 'Achiever', 'interests': 'Business/Leadership', 'wellbeing': 'Green',
                'soft_skills': 'Leadership-leaning, Strong time-management, Assertive',
                'msg': 'I am aiming for top grades in commerce and mathematics this term.'
            },
            {
                'username': 'ishaan_nair', 'email': 'ishaan.n@school.edu',
                'first_name': 'Ishaan', 'last_name': 'Nair',
                'tier': User.AcademicTier.SCHOOL, 'grade': '8th Grade',
                'institution': 'Oakridge International', 'color': '#ec4899',
                'v_bias': 3, 'k_bias': 5, 'a_bias': 2, 'g_bias': 4, 's_bias': 4, # High Stress
                'personality': 'Explorer', 'interests': 'Creative/Artistic', 'wellbeing': 'Amber',
                'soft_skills': 'Idea-generator, Needs pacing support, Accommodating',
                'msg': 'Sometimes long lectures without slides make me lose focus.'
            },
            {
                'username': 'tanya_kapoor', 'email': 'tanya.k@school.edu',
                'first_name': 'Tanya', 'last_name': 'Kapoor',
                'tier': User.AcademicTier.SCHOOL, 'grade': '12th Grade (Commerce)',
                'institution': 'DPS RK Puram', 'color': '#14b8a6',
                'v_bias': 2, 'k_bias': 2, 'a_bias': 4, 'g_bias': 4, 's_bias': 1,
                'personality': 'Collaborator', 'interests': 'Business/Leadership', 'wellbeing': 'Green',
                'soft_skills': 'Collaborative, Moderate time-management, Diplomatic',
                'msg': 'I like working on business model case studies and mock stock trading games.'
            },
            {
                'username': 'dev_malhotra', 'email': 'dev.m@school.edu',
                'first_name': 'Dev', 'last_name': 'Malhotra',
                'tier': User.AcademicTier.SCHOOL, 'grade': '9th Grade',
                'institution': 'The Heritage School', 'color': '#f43f5e',
                'v_bias': 4, 'k_bias': 1, 'a_bias': 2, 'g_bias': 3, 's_bias': 5, # High Stress
                'personality': 'Analyst', 'interests': 'STEM/Analytical', 'wellbeing': 'Red',
                'soft_skills': 'Independent/Reliable, Needs organization support, Conflict-avoidant',
                'msg': 'I feel overwhelmed when multiple subject assignments are due on the exact same Friday.'
            },

            # --- UNDERGRADUATE TIER (UG) - 10 Students ---
            {
                'username': 'maya_chen', 'email': 'maya.c@univ.edu',
                'first_name': 'Maya', 'last_name': 'Chen',
                'tier': User.AcademicTier.UG, 'grade': '3rd Year B.Tech Computer Science',
                'institution': 'Apex Institute of Technology', 'color': '#4f46e5',
                'v_bias': 4, 'k_bias': 5, 'a_bias': 2, 'g_bias': 5, 's_bias': 2,
                'personality': 'Hands-On Innovator', 'interests': 'STEM/Analytical', 'wellbeing': 'Green',
                'soft_skills': 'Idea-generator, Strong time-management, Assertive',
                'msg': 'Building full-stack web applications and algorithm visualization tools is my passion.'
            },
            {
                'username': 'liam_smith', 'email': 'liam.s@univ.edu',
                'first_name': 'Liam', 'last_name': 'Smith',
                'tier': User.AcademicTier.UG, 'grade': '2nd Year B.Des Interaction Design',
                'institution': 'National Institute of Design', 'color': '#06b6d4',
                'v_bias': 5, 'k_bias': 3, 'a_bias': 1, 'g_bias': 4, 's_bias': 2,
                'personality': 'Visual Strategist', 'interests': 'Creative/Artistic', 'wellbeing': 'Green',
                'soft_skills': 'Collaborative, Moderate time-management, Diplomatic',
                'msg': 'I understand UX architecture through wireframes, Figma components, and user journey flowcharts.'
            },
            {
                'username': 'priya_ramesh', 'email': 'priya.r@univ.edu',
                'first_name': 'Priya', 'last_name': 'Ramesh',
                'tier': User.AcademicTier.UG, 'grade': '4th Year B.Tech Mechanical',
                'institution': 'IIT Madras Campus', 'color': '#10b981',
                'v_bias': 3, 'k_bias': 5, 'a_bias': 2, 'g_bias': 5, 's_bias': 4, # High Stress (Graduation pressure)
                'personality': 'Hands-On Innovator', 'interests': 'STEM/Analytical', 'wellbeing': 'Amber',
                'soft_skills': 'Independent/Reliable, Strong time-management, Assertive',
                'msg': 'Final-year capstone project and placement interviews are creating a lot of deadline stacking.'
            },
            {
                'username': 'alex_turner', 'email': 'alex.t@univ.edu',
                'first_name': 'Alex', 'last_name': 'Turner',
                'tier': User.AcademicTier.UG, 'grade': '1st Year B.A. Political Science',
                'institution': 'Faculty of Social Sciences', 'color': '#f59e0b',
                'v_bias': 2, 'k_bias': 1, 'a_bias': 5, 'g_bias': 4, 's_bias': 1,
                'personality': 'Collaborator', 'interests': 'People/Social', 'wellbeing': 'Green',
                'soft_skills': 'Leadership-leaning, Moderate time-management, Diplomatic',
                'msg': 'I learn fastest during open seminar debates, podcast analysis, and collaborative presentations.'
            },
            {
                'username': 'siddharth_rao', 'email': 'sid.r@univ.edu',
                'first_name': 'Siddharth', 'last_name': 'Rao',
                'tier': User.AcademicTier.UG, 'grade': '3rd Year B.Sc Data Science',
                'institution': 'Symbiosis University', 'color': '#6366f1',
                'v_bias': 5, 'k_bias': 3, 'a_bias': 2, 'g_bias': 5, 's_bias': 1,
                'personality': 'Analyst', 'interests': 'STEM/Analytical', 'wellbeing': 'Green',
                'soft_skills': 'Independent/Reliable, Strong time-management, Assertive',
                'msg': 'I love working through statistical mechanics, Bayesian models, and Python data visualization.'
            },
            {
                'username': 'fatima_khan', 'email': 'fatima.k@univ.edu',
                'first_name': 'Fatima', 'last_name': 'Khan',
                'tier': User.AcademicTier.UG, 'grade': '2nd Year BBA Marketing',
                'institution': 'School of Business Studies', 'color': '#ec4899',
                'v_bias': 3, 'k_bias': 2, 'a_bias': 5, 'g_bias': 4, 's_bias': 2,
                'personality': 'Collaborator', 'interests': 'Business/Leadership', 'wellbeing': 'Green',
                'soft_skills': 'Leadership-leaning, Strong time-management, Assertive',
                'msg': 'I enjoy pitch presentations, marketing campaign simulations, and team sprint planning.'
            },
            {
                'username': 'vikram_singh', 'email': 'vikram.s@univ.edu',
                'first_name': 'Vikram', 'last_name': 'Singh',
                'tier': User.AcademicTier.UG, 'grade': '1st Year B.Tech Electrical',
                'institution': 'Vellore Institute', 'color': '#f43f5e',
                'v_bias': 2, 'k_bias': 3, 'a_bias': 2, 'g_bias': 3, 's_bias': 5, # High Stress
                'personality': 'Achiever', 'interests': 'STEM/Analytical', 'wellbeing': 'Red',
                'soft_skills': 'Independent/Reliable, Needs pacing support, Conflict-avoidant',
                'msg': 'Transitioning from high school to first-year university engineering courses has been very stressful for me.'
            },
            {
                'username': 'chloe_dupont', 'email': 'chloe.d@univ.edu',
                'first_name': 'Chloe', 'last_name': 'Dupont',
                'tier': User.AcademicTier.UG, 'grade': '3rd Year B.Sc Psychology',
                'institution': 'Liberal Arts College', 'color': '#14b8a6',
                'v_bias': 4, 'k_bias': 3, 'a_bias': 4, 'g_bias': 4, 's_bias': 2,
                'personality': 'Collaborator', 'interests': 'People/Social', 'wellbeing': 'Green',
                'soft_skills': 'Collaborative, Moderate time-management, Diplomatic',
                'msg': 'Interested in cognitive behavioral research and empirical observational methodology.'
            },
            {
                'username': 'rahul_iyer', 'email': 'rahul.i@univ.edu',
                'first_name': 'Rahul', 'last_name': 'Iyer',
                'tier': User.AcademicTier.UG, 'grade': '2nd Year B.Com Finance',
                'institution': 'St. Joseph College of Commerce', 'color': '#8b5cf6',
                'v_bias': 4, 'k_bias': 2, 'a_bias': 3, 'g_bias': 4, 's_bias': 2,
                'personality': 'Analyst', 'interests': 'Business/Leadership', 'wellbeing': 'Green',
                'soft_skills': 'Independent/Reliable, Strong time-management, Assertive',
                'msg': 'Spreadsheets, balance sheet modeling, and corporate valuation tables make complete sense to me.'
            },
            {
                'username': 'zoya_akhtar', 'email': 'zoya.a@univ.edu',
                'first_name': 'Zoya', 'last_name': 'Akhtar',
                'tier': User.AcademicTier.UG, 'grade': '4th Year B.Arch Architecture',
                'institution': 'School of Planning & Architecture', 'color': '#06b6d4',
                'v_bias': 5, 'k_bias': 5, 'a_bias': 2, 'g_bias': 5, 's_bias': 3,
                'personality': 'Visual Strategist', 'interests': 'Creative/Artistic', 'wellbeing': 'Green',
                'soft_skills': 'Idea-generator, Strong time-management, Assertive',
                'msg': 'I thrive when sketching physical 3D architectural models and analyzing structural load diagrams.'
            },

            # --- POSTGRADUATE TIER (PG) - 7 Students ---
            {
                'username': 'dr_arjun_nair', 'email': 'arjun.n@research.edu',
                'first_name': 'Arjun', 'last_name': 'Nair',
                'tier': User.AcademicTier.PG, 'grade': '2nd Year Ph.D. Neuroscience',
                'institution': 'National Brain Research Centre', 'color': '#8b5cf6',
                'v_bias': 4, 'k_bias': 4, 'a_bias': 3, 'g_bias': 5, 's_bias': 2,
                'personality': 'Analyst', 'interests': 'STEM/Analytical', 'wellbeing': 'Green',
                'soft_skills': 'Independent/Reliable, Strong time-management, Assertive',
                'msg': 'Drafting journal submissions for computational neural modeling. Value rigorous theoretical critique.'
            },
            {
                'username': 'meera_krishnan', 'email': 'meera.k@mba.edu',
                'first_name': 'Meera', 'last_name': 'Krishnan',
                'tier': User.AcademicTier.PG, 'grade': '2nd Year MBA Executive',
                'institution': 'Indian Institute of Management', 'color': '#10b981',
                'v_bias': 4, 'k_bias': 2, 'a_bias': 5, 'g_bias': 5, 's_bias': 1,
                'personality': 'Achiever', 'interests': 'Business/Leadership', 'wellbeing': 'Green',
                'soft_skills': 'Leadership-leaning, Strong time-management, Assertive',
                'msg': 'Focusing on venture capital term-sheet negotiations and executive strategy simulations.'
            },
            {
                'username': 'david_kim', 'email': 'david.k@grad.edu',
                'first_name': 'David', 'last_name': 'Kim',
                'tier': User.AcademicTier.PG, 'grade': '1st Year M.S. Artificial Intelligence',
                'institution': 'Global Tech University', 'color': '#3b82f6',
                'v_bias': 4, 'k_bias': 5, 'a_bias': 2, 'g_bias': 5, 's_bias': 3,
                'personality': 'Hands-On Innovator', 'interests': 'STEM/Analytical', 'wellbeing': 'Green',
                'soft_skills': 'Idea-generator, Strong time-management, Assertive',
                'msg': 'Training transformer models and distributed GPU pipeline tuning are my main research projects.'
            },
            {
                'username': 'shreya_mukherjee', 'email': 'shreya.m@research.edu',
                'first_name': 'Shreya', 'last_name': 'Mukherjee',
                'tier': User.AcademicTier.PG, 'grade': '3rd Year Ph.D. Economics',
                'institution': 'Delhi School of Economics', 'color': '#f43f5e',
                'v_bias': 4, 'k_bias': 2, 'a_bias': 3, 'g_bias': 4, 's_bias': 5, # High Stress (Dissertation Defense)
                'personality': 'Analyst', 'interests': 'STEM/Analytical', 'wellbeing': 'Red',
                'soft_skills': 'Independent/Reliable, Needs pacing support, Accommodating',
                'msg': 'Thesis defense deadline is approaching in 6 weeks. Experiencing severe burnout and manuscript fatigue.'
            },
            {
                'username': 'neil_bose', 'email': 'neil.b@grad.edu',
                'first_name': 'Neil', 'last_name': 'Bose',
                'tier': User.AcademicTier.PG, 'grade': '1st Year M.Tech Robotics',
                'institution': 'IIT Bombay Campus', 'color': '#f59e0b',
                'v_bias': 3, 'k_bias': 5, 'a_bias': 2, 'g_bias': 4, 's_bias': 2,
                'personality': 'Hands-On Innovator', 'interests': 'STEM/Analytical', 'wellbeing': 'Green',
                'soft_skills': 'Idea-generator, Moderate time-management, Assertive',
                'msg': 'Hardware kinematics test rigs and ROS2 firmware simulation are my core domains.'
            },
            {
                'username': 'amara_okoye', 'email': 'amara.o@grad.edu',
                'first_name': 'Amara', 'last_name': 'Okoye',
                'tier': User.AcademicTier.PG, 'grade': '2nd Year M.Sc Public Health',
                'institution': 'Global Health Institute', 'color': '#06b6d4',
                'v_bias': 3, 'k_bias': 3, 'a_bias': 5, 'g_bias': 5, 's_bias': 2,
                'personality': 'Collaborator', 'interests': 'People/Social', 'wellbeing': 'Green',
                'soft_skills': 'Leadership-leaning, Strong time-management, Diplomatic',
                'msg': 'Epidemiological field studies and community healthcare surveys are my area of specialization.'
            },
            {
                'username': 'karthik_reddy', 'email': 'karthik.r@grad.edu',
                'first_name': 'Karthik', 'last_name': 'Reddy',
                'tier': User.AcademicTier.PG, 'grade': '1st Year M.Des Strategic Design',
                'institution': 'Design Innovation Centre', 'color': '#14b8a6',
                'v_bias': 5, 'k_bias': 4, 'a_bias': 3, 'g_bias': 4, 's_bias': 2,
                'personality': 'Visual Strategist', 'interests': 'Creative/Artistic', 'wellbeing': 'Green',
                'soft_skills': 'Idea-generator, Strong time-management, Diplomatic',
                'msg': 'I translate systemic market problems into speculative design blueprints and stakeholder journey maps.'
            }
        ]

        # 3. Create Students and Submissions in Database
        seeded_count = 0
        for s_data in students_roster:
            student_user, _ = User.objects.get_or_create(
                username=s_data['username'],
                defaults={
                    'email': s_data['email'],
                    'first_name': s_data['first_name'],
                    'last_name': s_data['last_name'],
                    'role': User.Role.STUDENT,
                    'academic_tier': s_data['tier'],
                    'grade_or_year': s_data['grade'],
                    'institution': s_data['institution'],
                    'avatar_color': s_data['color']
                }
            )
            student_user.set_password('Password123!')
            student_user.save()

            # Clean previous submissions to re-seed fresh
            Submission.objects.filter(student=student_user).delete()

            # Fetch active questions for this student's tier
            questions = Question.objects.filter(tier=s_data['tier'], is_active=True)

            selected_choices = []
            for q in questions:
                choices = list(q.choices.all())
                if not choices:
                    continue

                # Pick choice aligned with student's bias
                if q.section == Question.Section.PART_1:
                    # Pick correct answer with 85% probability for high growth students
                    correct_choices = [c for c in choices if c.is_correct]
                    if correct_choices and random.random() < 0.85:
                        chosen = correct_choices[0]
                    else:
                        chosen = random.choice(choices)
                else: # Part 2 Whole-Student Profile
                    # Match tag if available
                    matched = [c for c in choices if c.tag in [s_data['personality'], s_data['interests'], s_data['wellbeing']]]
                    if matched:
                        chosen = matched[0]
                    else:
                        chosen = random.choice(choices)

                selected_choices.append(chosen)

            # Compute scores
            scores = compute_psychometric_scores(selected_choices)
            # Apply bias adjustments to ensure rich spread
            scores['visual_score'] = min(100, max(20, scores['visual_score'] + (s_data['v_bias'] - 3) * 12))
            scores['kinesthetic_score'] = min(100, max(20, scores['kinesthetic_score'] + (s_data['k_bias'] - 3) * 12))
            scores['auditory_score'] = min(100, max(20, scores['auditory_score'] + (s_data['a_bias'] - 3) * 12))
            scores['growth_score'] = min(100, max(30, scores['growth_score'] + (s_data['g_bias'] - 3) * 10))
            scores['stress_score'] = min(100, max(15, (s_data['s_bias'] * 18) + random.randint(-4, 4)))

            persona = determine_persona(scores)
            playbook = generate_teacher_playbook(scores, persona, wellbeing_flag=s_data['wellbeing'])

            cognitive_correct = sum(1 for c in selected_choices if c.is_correct)
            cognitive_total = sum(1 for c in selected_choices if c.question.choices.filter(is_correct=True).exists())
            cognitive_accuracy = round((cognitive_correct / max(cognitive_total, 1)) * 100)

            submission = Submission.objects.create(
                student=student_user,
                tier=s_data['tier'],
                visual_score=scores['visual_score'],
                auditory_score=scores['auditory_score'],
                kinesthetic_score=scores['kinesthetic_score'],
                growth_score=scores['growth_score'],
                stress_score=scores['stress_score'],
                cognitive_score=cognitive_accuracy,
                personality_tag=s_data['personality'],
                interests_tag=s_data['interests'],
                wellbeing_flag=s_data['wellbeing'],
                soft_skills_summary=s_data['soft_skills'],
                open_message_to_teacher=s_data['msg'],
                persona_title=persona['title'],
                persona_tagline=persona['tagline'],
                persona_summary=persona['summary'],
                teacher_motivation=playbook['motivation'],
                teacher_communication=playbook['communication'],
                teacher_caution=playbook['caution']
            )

            # Create answers
            answers_to_create = [
                SubmissionAnswer(
                    submission=submission,
                    question=choice.question,
                    selected_choice=choice
                )
                for choice in selected_choices
            ]
            SubmissionAnswer.objects.bulk_create(answers_to_create)

            # Seed 1-2 private teacher observation notes on selected high-risk or champion students
            if s_data['wellbeing'] == 'Red':
                TeacherNote.objects.create(
                    teacher=teacher,
                    student=student_user,
                    submission=submission,
                    category=TeacherNote.Category.WELLBEING,
                    content=f"Observed elevated anxiety markers. Scheduled a 15-minute 1-on-1 check-in before the upcoming evaluation."
                )
            elif s_data['g_bias'] == 5:
                TeacherNote.objects.create(
                    teacher=teacher,
                    student=student_user,
                    submission=submission,
                    category=TeacherNote.Category.ACADEMIC,
                    content=f"Exhibits strong {s_data['personality']} leadership and robust problem-solving instincts. Candidate for research group leadership."
                )

            seeded_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Successfully seeded {seeded_count} realistic student profiles, submissions, and teacher notes!"
        ))

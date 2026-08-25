from django.core.management.base import BaseCommand
from apps.assessments.models import Question, Choice
from apps.accounts.models import User

class Command(BaseCommand):
    help = 'Seeds complete question bank from Adaptive Screening Test & Whole-Student Profile PDF.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Seeding Adaptive Screening & Whole-Student Profile Question Bank...'))

        Question.objects.all().delete()

        # =========================================================================
        # 1. PART 2: WHOLE-STUDENT PROFILE (Shared across all tiers)
        # =========================================================================
        shared_profile_questions = [
            # Personality Probes (Achiever / Explorer / Collaborator / Analyst)
            {
                'category': Question.Category.PERSONALITY,
                'section': Question.Section.PART_2,
                'order': 1,
                'prompt': 'When starting a new project or assignment, I usually:',
                'subtitle': 'Personality Style & Project Initiation',
                'choices': [
                    {'text': 'Set clear goals and track progress until it’s done', 'tag': 'Achiever', 'g': 4, 'v': 3, 'k': 2, 'a': 1, 's': 1},
                    {'text': 'Look for a new or different way to approach it', 'tag': 'Explorer', 'g': 5, 'v': 2, 'k': 4, 'a': 2, 's': 1},
                    {'text': 'Prefer to work with others and share ideas', 'tag': 'Collaborator', 'g': 3, 'v': 1, 'k': 2, 'a': 5, 's': 1},
                    {'text': 'Research thoroughly before starting', 'tag': 'Analyst', 'g': 4, 'v': 4, 'k': 1, 'a': 2, 's': 1},
                ]
            },
            {
                'category': Question.Category.PERSONALITY,
                'section': Question.Section.PART_2,
                'order': 2,
                'prompt': 'I feel most satisfied when:',
                'subtitle': 'Intrinsic Motivation & Reward Driver',
                'choices': [
                    {'text': 'I complete a task and see the result', 'tag': 'Achiever', 'g': 4, 'v': 3, 'k': 3, 'a': 1, 's': 1},
                    {'text': 'I discover something new or unexpected', 'tag': 'Explorer', 'g': 5, 'v': 2, 'k': 4, 'a': 2, 's': 1},
                    {'text': 'A team succeeds together', 'tag': 'Collaborator', 'g': 4, 'v': 1, 'k': 2, 'a': 5, 's': 1},
                    {'text': 'I fully understand how or why something works', 'tag': 'Analyst', 'g': 5, 'v': 4, 'k': 2, 'a': 2, 's': 1},
                ]
            },
            {
                'category': Question.Category.PERSONALITY,
                'section': Question.Section.PART_2,
                'order': 3,
                'prompt': 'If a plan doesn’t work, I tend to:',
                'subtitle': 'Resilience & Problem Solving Approach',
                'choices': [
                    {'text': 'Push harder and reach the goal a different way', 'tag': 'Achiever', 'g': 4, 'v': 2, 'k': 4, 'a': 1, 's': 2},
                    {'text': 'Try a completely new approach', 'tag': 'Explorer', 'g': 5, 'v': 2, 'k': 4, 'a': 2, 's': 1},
                    {'text': 'Ask others for input or help', 'tag': 'Collaborator', 'g': 4, 'v': 1, 'k': 1, 'a': 5, 's': 2},
                    {'text': 'Step back and analyze what went wrong first', 'tag': 'Analyst', 'g': 5, 'v': 4, 'k': 1, 'a': 2, 's': 1},
                ]
            },

            # Interests & Career Inclination (STEM / Creative / People / Business)
            {
                'category': Question.Category.INTERESTS,
                'section': Question.Section.PART_2,
                'order': 4,
                'prompt': 'Which activity would you enjoy most?',
                'subtitle': 'Core Interest & Inclination',
                'choices': [
                    {'text': 'Solving a tricky puzzle or problem', 'tag': 'STEM/Analytical', 'g': 4, 'v': 4, 'k': 4, 'a': 1, 's': 1},
                    {'text': 'Designing, writing, or creating something original', 'tag': 'Creative/Artistic', 'g': 4, 'v': 5, 'k': 3, 'a': 2, 's': 1},
                    {'text': 'Helping, teaching, or organizing a group of people', 'tag': 'People/Social', 'g': 4, 'v': 1, 'k': 2, 'a': 5, 's': 1},
                    {'text': 'Planning a project or pitching an idea', 'tag': 'Business/Leadership', 'g': 4, 'v': 3, 'k': 2, 'a': 4, 's': 1},
                ]
            },
            {
                'category': Question.Category.INTERESTS,
                'section': Question.Section.PART_2,
                'order': 5,
                'prompt': 'In free time, I’m most drawn to:',
                'subtitle': 'Leisure & Organic Curiosity',
                'choices': [
                    {'text': 'Science, technology, or how things work', 'tag': 'STEM/Analytical', 'g': 4, 'v': 4, 'k': 4, 'a': 1, 's': 1},
                    {'text': 'Art, music, writing, or design', 'tag': 'Creative/Artistic', 'g': 4, 'v': 5, 'k': 3, 'a': 2, 's': 1},
                    {'text': 'Volunteering, mentoring, or community activities', 'tag': 'People/Social', 'g': 4, 'v': 1, 'k': 2, 'a': 5, 's': 1},
                    {'text': 'Starting projects, competitions, or ventures', 'tag': 'Business/Leadership', 'g': 5, 'v': 3, 'k': 3, 'a': 3, 's': 1},
                ]
            },

            # Wellbeing & Motivation (Green A/B, Amber mixed, Red C/D)
            {
                'category': Question.Category.WELLBEING,
                'section': Question.Section.PART_2,
                'order': 6,
                'prompt': 'How confident do you feel about keeping up with your coursework right now?',
                'subtitle': 'Academic Self-Efficacy',
                'choices': [
                    {'text': 'Very confident', 'tag': 'Green', 'g': 5, 'v': 2, 'k': 2, 'a': 2, 's': 0},
                    {'text': 'Somewhat confident', 'tag': 'Green', 'g': 4, 'v': 2, 'k': 2, 'a': 2, 's': 1},
                    {'text': 'Somewhat worried', 'tag': 'Amber', 'g': 3, 'v': 2, 'k': 2, 'a': 2, 's': 3},
                    {'text': 'Very worried', 'tag': 'Red', 'g': 1, 'v': 1, 'k': 1, 'a': 1, 's': 5},
                ]
            },
            {
                'category': Question.Category.WELLBEING,
                'section': Question.Section.PART_2,
                'order': 7,
                'prompt': 'How motivated do you feel about your studies at the moment?',
                'subtitle': 'Current Academic Motivation',
                'choices': [
                    {'text': 'Very motivated', 'tag': 'Green', 'g': 5, 'v': 2, 'k': 2, 'a': 2, 's': 0},
                    {'text': 'Somewhat motivated', 'tag': 'Green', 'g': 4, 'v': 2, 'k': 2, 'a': 2, 's': 1},
                    {'text': 'Low motivation', 'tag': 'Amber', 'g': 2, 'v': 1, 'k': 1, 'a': 1, 's': 3},
                    {'text': 'Struggling to stay motivated', 'tag': 'Red', 'g': 1, 'v': 1, 'k': 1, 'a': 1, 's': 5},
                ]
            },
            {
                'category': Question.Category.WELLBEING,
                'section': Question.Section.PART_2,
                'order': 8,
                'prompt': 'How manageable does your current workload/stress feel?',
                'subtitle': 'Workload & Stress Perception',
                'choices': [
                    {'text': 'Very manageable', 'tag': 'Green', 'g': 5, 'v': 2, 'k': 2, 'a': 2, 's': 0},
                    {'text': 'Mostly manageable', 'tag': 'Green', 'g': 4, 'v': 2, 'k': 2, 'a': 2, 's': 1},
                    {'text': 'Often overwhelming', 'tag': 'Amber', 'g': 2, 'v': 1, 'k': 1, 'a': 1, 's': 4},
                    {'text': 'Constantly overwhelming', 'tag': 'Red', 'g': 1, 'v': 1, 'k': 1, 'a': 1, 's': 5},
                ]
            },

            # Soft Skills & Behavior
            {
                'category': Question.Category.SOFTSKILLS,
                'section': Question.Section.PART_2,
                'order': 9,
                'prompt': 'When working on a group task, I usually:',
                'subtitle': 'Team Role Dynamics',
                'choices': [
                    {'text': 'Take the lead and organize the group (Leadership-leaning)', 'tag': 'Leadership-leaning', 'g': 4, 'v': 3, 'k': 2, 'a': 4, 's': 1},
                    {'text': 'Focus on getting my part done well (Independent/Reliable)', 'tag': 'Independent/Reliable', 'g': 4, 'v': 3, 'k': 4, 'a': 1, 's': 1},
                    {'text': 'Help resolve disagreements and keep the group positive (Collaborative)', 'tag': 'Collaborative', 'g': 4, 'v': 1, 'k': 2, 'a': 5, 's': 1},
                    {'text': 'Prefer contributing ideas over managing logistics (Idea-generator)', 'tag': 'Idea-generator', 'g': 4, 'v': 4, 'k': 3, 'a': 3, 's': 1},
                ]
            },
            {
                'category': Question.Category.SOFTSKILLS,
                'section': Question.Section.PART_2,
                'order': 10,
                'prompt': 'My approach to deadlines is usually:',
                'subtitle': 'Time Management & Execution Style',
                'choices': [
                    {'text': 'I plan ahead and finish early (Strong time-management)', 'tag': 'Strong time-management', 'g': 5, 'v': 4, 'k': 3, 'a': 2, 's': 0},
                    {'text': 'I work steadily and finish on time (Moderate time-management)', 'tag': 'Moderate time-management', 'g': 4, 'v': 3, 'k': 3, 'a': 2, 's': 1},
                    {'text': 'I tend to do most of it close to the deadline (Needs pacing support)', 'tag': 'Needs pacing support', 'g': 3, 'v': 2, 'k': 3, 'a': 2, 's': 3},
                    {'text': 'I often need reminders or extensions (Needs organization support)', 'tag': 'Needs organization support', 'g': 2, 'v': 1, 'k': 1, 'a': 1, 's': 4},
                ]
            },
            {
                'category': Question.Category.SOFTSKILLS,
                'section': Question.Section.PART_2,
                'order': 11,
                'prompt': 'When I disagree with someone in a group, I usually:',
                'subtitle': 'Conflict Resolution Style',
                'choices': [
                    {'text': 'State my view clearly and try to persuade them (Assertive)', 'tag': 'Assertive', 'g': 4, 'v': 2, 'k': 2, 'a': 4, 's': 1},
                    {'text': 'Listen first, then share my perspective (Diplomatic)', 'tag': 'Diplomatic', 'g': 5, 'v': 2, 'k': 2, 'a': 5, 's': 1},
                    {'text': 'Go along with the group to avoid conflict (Accommodating)', 'tag': 'Accommodating', 'g': 3, 'v': 1, 'k': 1, 'a': 3, 's': 3},
                    {'text': 'Avoid the discussion if possible (Conflict-avoidant)', 'tag': 'Conflict-avoidant', 'g': 2, 'v': 1, 'k': 1, 'a': 1, 's': 4},
                ]
            },
        ]

        # Seed shared profile questions into each tier
        for tier in [User.AcademicTier.SCHOOL, User.AcademicTier.UG, User.AcademicTier.PG]:
            for q_data in shared_profile_questions:
                q_prompt = q_data['prompt']
                # Elective vs Career question variation by tier
                if q_data['order'] == 5:
                    pass # Keep standard

                q = Question.objects.create(
                    tier=tier,
                    section=q_data['section'],
                    category=q_data['category'],
                    difficulty=Question.Difficulty.GENERAL,
                    order=q_data['order'],
                    prompt=q_prompt,
                    subtitle=q_data['subtitle'],
                    is_active=True
                )
                for idx, c_data in enumerate(q_data['choices'], start=1):
                    Choice.objects.create(
                        question=q,
                        text=c_data['text'],
                        order=idx,
                        tag=c_data.get('tag', ''),
                        visual_weight=c_data.get('v', 0),
                        auditory_weight=c_data.get('a', 0),
                        kinesthetic_weight=c_data.get('k', 0),
                        growth_weight=c_data.get('g', 0),
                        stress_weight=c_data.get('s', 0)
                    )

            # Add Q3 for Interests (Elective for School, Career for UG/PG)
            if tier == User.AcademicTier.SCHOOL:
                elective_q = Question.objects.create(
                    tier=tier,
                    section=Question.Section.PART_2,
                    category=Question.Category.INTERESTS,
                    difficulty=Question.Difficulty.GENERAL,
                    order=12,
                    prompt='If you could pick one elective to explore deeply, it would be:',
                    subtitle='Academic Elective Preference',
                    is_active=True
                )
                Choice.objects.create(question=elective_q, order=1, text='Math / Science / Computer Science', tag='STEM/Analytical', visual_weight=4, kinesthetic_weight=4, growth_weight=4)
                Choice.objects.create(question=elective_q, order=2, text='Art / Music / Literature', tag='Creative/Artistic', visual_weight=5, auditory_weight=3, growth_weight=4)
                Choice.objects.create(question=elective_q, order=3, text='Psychology / Social Studies / Languages', tag='People/Social', auditory_weight=4, visual_weight=2, growth_weight=4)
                Choice.objects.create(question=elective_q, order=4, text='Economics / Business Studies', tag='Business/Leadership', visual_weight=3, auditory_weight=3, growth_weight=4)
            else:
                career_q = Question.objects.create(
                    tier=tier,
                    section=Question.Section.PART_2,
                    category=Question.Category.INTERESTS,
                    difficulty=Question.Difficulty.GENERAL,
                    order=12,
                    prompt='Which career field appeals to you most right now?',
                    subtitle='Career Inclination',
                    is_active=True
                )
                Choice.objects.create(question=career_q, order=1, text='Engineering / Data / Research', tag='STEM/Analytical', visual_weight=4, kinesthetic_weight=4, growth_weight=4)
                Choice.objects.create(question=career_q, order=2, text='Design / Media / Content', tag='Creative/Artistic', visual_weight=5, auditory_weight=3, growth_weight=4)
                Choice.objects.create(question=career_q, order=3, text='Education / Healthcare / Social Work', tag='People/Social', auditory_weight=4, visual_weight=2, growth_weight=4)
                Choice.objects.create(question=career_q, order=4, text='Business / Management / Entrepreneurship', tag='Business/Leadership', visual_weight=3, auditory_weight=3, growth_weight=4)


        # =========================================================================
        # 2. PART 1: CORE ADAPTIVE TEST BY TIER (School, UG, PG)
        # =========================================================================

        # ------------------- SCHOOL TIER (Grade 8-12) -------------------
        school_adaptive = [
            # Reading Comprehension
            {
                'category': Question.Category.READING,
                'difficulty': Question.Difficulty.EASY,
                'order': 101,
                'prompt': '“Meera plants a sapling every year on her birthday to see how much it has grown. This year, for the first time, the tree is taller than her.” What is this passage mainly about?',
                'subtitle': 'Reading Comprehension (Easy)',
                'choices': [
                    {'text': 'A birthday party', 'is_correct': False},
                    {'text': 'Meera tracking a tree’s growth over the years', 'is_correct': True, 'g': 4, 'v': 3},
                    {'text': 'Meera being afraid of trees', 'is_correct': False},
                    {'text': 'A gardening competition', 'is_correct': False},
                ]
            },
            {
                'category': Question.Category.READING,
                'difficulty': Question.Difficulty.MEDIUM,
                'order': 102,
                'prompt': '“The city council debated the new park for months. Some wanted more benches, others wanted more trees. In the end, they built a park with both — just fewer of each than originally planned.” What does this best show?',
                'subtitle': 'Reading Comprehension (Medium)',
                'choices': [
                    {'text': 'The council couldn’t agree on anything', 'is_correct': False},
                    {'text': 'A compromise was reached between two competing preferences', 'is_correct': True, 'g': 4, 'v': 3, 'a': 3},
                    {'text': 'The park was cancelled', 'is_correct': False},
                    {'text': 'Trees are more important than benches', 'is_correct': False},
                ]
            },
            {
                'category': Question.Category.READING,
                'difficulty': Question.Difficulty.HARD,
                'order': 103,
                'prompt': '“Despite the coach’s warnings, the team kept playing an aggressive style. They won more matches, but injuries piled up, and by the season’s end, three key players were out.” What’s the most reasonable takeaway?',
                'subtitle': 'Reading Comprehension (Hard)',
                'choices': [
                    {'text': 'Aggressive play should always be avoided', 'is_correct': False},
                    {'text': 'The coach was wrong to warn them', 'is_correct': False},
                    {'text': 'Their success came with a real cost they’ll likely feel next season', 'is_correct': True, 'g': 5, 'v': 3},
                    {'text': 'Injuries have nothing to do with playing style', 'is_correct': False},
                ]
            },

            # General Awareness
            {
                'category': Question.Category.AWARENESS,
                'difficulty': Question.Difficulty.EASY,
                'order': 104,
                'prompt': 'Which of these is a renewable source of energy?',
                'subtitle': 'General Awareness (Easy)',
                'choices': [
                    {'text': 'Coal', 'is_correct': False},
                    {'text': 'Solar', 'is_correct': True, 'g': 4, 'k': 3},
                    {'text': 'Petroleum', 'is_correct': False},
                    {'text': 'Natural gas', 'is_correct': False},
                ]
            },
            {
                'category': Question.Category.AWARENESS,
                'difficulty': Question.Difficulty.MEDIUM,
                'order': 105,
                'prompt': 'If a region’s population grows much faster than its food production, what’s the likely long-term challenge?',
                'subtitle': 'General Awareness (Medium)',
                'choices': [
                    {'text': 'Lower food prices', 'is_correct': False},
                    {'text': 'Food scarcity', 'is_correct': True, 'g': 4, 'v': 3},
                    {'text': 'Less need for farming', 'is_correct': False},
                    {'text': 'Higher food security', 'is_correct': False},
                ]
            },
            {
                'category': Question.Category.AWARENESS,
                'difficulty': Question.Difficulty.HARD,
                'order': 106,
                'prompt': 'A city bans single-use plastic bags. Which outcome is least likely to happen as a direct result?',
                'subtitle': 'General Awareness (Hard)',
                'choices': [
                    {'text': 'Reduced landfill waste', 'is_correct': False},
                    {'text': 'More people using reusable bags', 'is_correct': False},
                    {'text': 'Complete elimination of all pollution in the city', 'is_correct': True, 'g': 5, 'v': 4},
                    {'text': 'Some short-term inconvenience for shoppers', 'is_correct': False},
                ]
            },

            # Pattern & Code Reasoning
            {
                'category': Question.Category.PATTERN,
                'difficulty': Question.Difficulty.EASY,
                'order': 107,
                'prompt': 'What comes next in the sequence: A, C, E, G, ___?',
                'subtitle': 'Pattern Reasoning (Easy)',
                'choices': [
                    {'text': 'H', 'is_correct': False},
                    {'text': 'I', 'is_correct': True, 'g': 4, 'v': 4},
                    {'text': 'F', 'is_correct': False},
                    {'text': 'J', 'is_correct': False},
                ]
            },
            {
                'category': Question.Category.PATTERN,
                'difficulty': Question.Difficulty.MEDIUM,
                'order': 108,
                'prompt': 'Which one doesn’t belong: BDF, CEG, ACE, BCD?',
                'subtitle': 'Code Reasoning (Medium)',
                'choices': [
                    {'text': 'BDF', 'is_correct': False},
                    {'text': 'CEG', 'is_correct': False},
                    {'text': 'ACE', 'is_correct': False},
                    {'text': 'BCD', 'is_correct': True, 'g': 4, 'v': 4},
                ]
            },
            {
                'category': Question.Category.PATTERN,
                'difficulty': Question.Difficulty.HARD,
                'order': 109,
                'prompt': 'In a code, CAT is written as DBU (each letter shifted forward by one). How is DOG written in the same code?',
                'subtitle': 'Cipher Reasoning (Hard)',
                'choices': [
                    {'text': 'EPG', 'is_correct': False},
                    {'text': 'EPH', 'is_correct': True, 'g': 5, 'v': 4},
                    {'text': 'DPH', 'is_correct': False},
                    {'text': 'EOH', 'is_correct': False},
                ]
            },

            # Verbal / Logical Reasoning
            {
                'category': Question.Category.LOGIC,
                'difficulty': Question.Difficulty.EASY,
                'order': 110,
                'prompt': 'Book is to Read as Song is to ___?',
                'subtitle': 'Logical Analogy (Easy)',
                'choices': [
                    {'text': 'Sing', 'is_correct': False},
                    {'text': 'Listen', 'is_correct': True, 'g': 4, 'a': 4},
                    {'text': 'Write', 'is_correct': False},
                    {'text': 'Play', 'is_correct': False},
                ]
            },
            {
                'category': Question.Category.LOGIC,
                'difficulty': Question.Difficulty.MEDIUM,
                'order': 111,
                'prompt': 'All squares are rectangles. All rectangles have four sides. Therefore:',
                'subtitle': 'Deductive Logic (Medium)',
                'choices': [
                    {'text': 'All rectangles are squares', 'is_correct': False},
                    {'text': 'All squares have four sides', 'is_correct': True, 'g': 4, 'v': 3},
                    {'text': 'All four-sided shapes are squares', 'is_correct': False},
                    {'text': 'No conclusion possible', 'is_correct': False},
                ]
            },
            {
                'category': Question.Category.LOGIC,
                'difficulty': Question.Difficulty.HARD,
                'order': 112,
                'prompt': 'Some Zips are Zaps. All Zaps are Zoos. Which must be true?',
                'subtitle': 'Syllogism Logic (Hard)',
                'choices': [
                    {'text': 'All Zips are Zoos', 'is_correct': False},
                    {'text': 'Some Zips are Zoos', 'is_correct': True, 'g': 5, 'v': 4},
                    {'text': 'No Zips are Zoos', 'is_correct': False},
                    {'text': 'All Zoos are Zips', 'is_correct': False},
                ]
            },

            # Learning Style Probes (VARK)
            {
                'category': Question.Category.VARK,
                'difficulty': Question.Difficulty.GENERAL,
                'order': 113,
                'prompt': 'When learning a new concept, I understand it best when I:',
                'subtitle': 'Learning Modality Probe 1',
                'choices': [
                    {'text': 'See a diagram or graph of it', 'v': 5, 'a': 1, 'k': 1, 'g': 3},
                    {'text': 'Read a step-by-step written explanation', 'v': 3, 'a': 4, 'k': 1, 'g': 3},
                    {'text': 'Work through a real example myself', 'v': 1, 'a': 1, 'k': 5, 'g': 4},
                    {'text': 'Think about why it works before using it', 'v': 3, 'a': 2, 'k': 2, 'g': 5},
                ]
            },
            {
                'category': Question.Category.VARK,
                'difficulty': Question.Difficulty.GENERAL,
                'order': 114,
                'prompt': 'When I get stuck on a problem, I usually:',
                'subtitle': 'Learning Modality Probe 2',
                'choices': [
                    {'text': 'Look for a visual pattern', 'v': 5, 'a': 1, 'k': 2, 'g': 3},
                    {'text': 'Re-read the question carefully', 'v': 2, 'a': 4, 'k': 1, 'g': 3},
                    {'text': 'Try different things until something works', 'v': 1, 'a': 1, 'k': 5, 'g': 4},
                    {'text': 'Pause and think through the underlying logic', 'v': 3, 'a': 2, 'k': 2, 'g': 5},
                ]
            },
            {
                'category': Question.Category.VARK,
                'difficulty': Question.Difficulty.GENERAL,
                'order': 115,
                'prompt': 'I remember what I study best through:',
                'subtitle': 'Learning Modality Probe 3',
                'choices': [
                    {'text': 'Charts and color-coding', 'v': 5, 'a': 1, 'k': 2, 'g': 3},
                    {'text': 'Notes and written definitions', 'v': 3, 'a': 4, 'k': 1, 'g': 3},
                    {'text': 'Practice and doing', 'v': 1, 'a': 1, 'k': 5, 'g': 4},
                    {'text': 'Working out the reasoning myself before checking answers', 'v': 3, 'a': 2, 'k': 2, 'g': 5},
                ]
            },
        ]

        # ------------------- UNDERGRADUATE TIER (UG) -------------------
        ug_adaptive = [
            # Reading Comprehension
            {
                'category': Question.Category.READING,
                'difficulty': Question.Difficulty.EASY,
                'order': 101,
                'prompt': '“A startup pivots its product twice within its first year based on user feedback.” What does this most likely indicate?',
                'subtitle': 'Reading Comprehension (Easy)',
                'choices': [
                    {'text': 'The founders are indecisive and directionless', 'is_correct': False},
                    {'text': 'The team is responsive to market signals', 'is_correct': True, 'g': 4, 'v': 3},
                    {'text': 'The product idea was bad from the start', 'is_correct': False},
                    {'text': 'Pivoting always guarantees success', 'is_correct': False},
                ]
            },
            {
                'category': Question.Category.READING,
                'difficulty': Question.Difficulty.MEDIUM,
                'order': 102,
                'prompt': '“Despite strong quarterly profits, a company’s stock price fell after the earnings call.” What’s the most likely explanation?',
                'subtitle': 'Reading Comprehension (Medium)',
                'choices': [
                    {'text': 'The market ignores profits entirely', 'is_correct': False},
                    {'text': 'Investor expectations were higher than actual results', 'is_correct': True, 'g': 4, 'v': 4},
                    {'text': 'Profit and stock price are unrelated', 'is_correct': False},
                    {'text': 'The report contained a math error', 'is_correct': False},
                ]
            },
            {
                'category': Question.Category.READING,
                'difficulty': Question.Difficulty.HARD,
                'order': 103,
                'prompt': '“A researcher’s paper concludes ‘X causes Y’ based solely on a survey showing X and Y often occur together.” What is the strongest critique of this conclusion?',
                'subtitle': 'Reading Comprehension (Hard)',
                'choices': [
                    {'text': 'Surveys are illegal', 'is_correct': False},
                    {'text': 'Correlation shown in a survey doesn’t establish causation', 'is_correct': True, 'g': 5, 'v': 4},
                    {'text': 'Y should have been studied instead', 'is_correct': False},
                    {'text': 'The researcher should have used more colors in the chart', 'is_correct': False},
                ]
            },

            # General Awareness
            {
                'category': Question.Category.AWARENESS,
                'difficulty': Question.Difficulty.EASY,
                'order': 104,
                'prompt': 'Which of these is typically considered a “soft skill” in a workplace?',
                'subtitle': 'General Awareness (Easy)',
                'choices': [
                    {'text': 'Coding in Python', 'is_correct': False},
                    {'text': 'Communication', 'is_correct': True, 'g': 4, 'a': 4},
                    {'text': 'Operating machinery', 'is_correct': False},
                    {'text': 'Data entry speed', 'is_correct': False},
                ]
            },
            {
                'category': Question.Category.AWARENESS,
                'difficulty': Question.Difficulty.MEDIUM,
                'order': 105,
                'prompt': 'A rise in interest rates set by a central bank generally aims to:',
                'subtitle': 'General Awareness (Medium)',
                'choices': [
                    {'text': 'Encourage more borrowing', 'is_correct': False},
                    {'text': 'Control inflation by discouraging excess borrowing', 'is_correct': True, 'g': 4, 'v': 3},
                    {'text': 'Increase government spending directly', 'is_correct': False},
                    {'text': 'Devalue the currency intentionally', 'is_correct': False},
                ]
            },
            {
                'category': Question.Category.AWARENESS,
                'difficulty': Question.Difficulty.HARD,
                'order': 106,
                'prompt': 'A company outsources part of its production to cut costs, but faces backlash over labor conditions at the supplier. This illustrates a tension between:',
                'subtitle': 'General Awareness (Hard)',
                'choices': [
                    {'text': 'Innovation and tradition', 'is_correct': False},
                    {'text': 'Cost efficiency and ethical responsibility', 'is_correct': True, 'g': 5, 'v': 3},
                    {'text': 'Marketing and sales', 'is_correct': False},
                    {'text': 'Local and global taxation', 'is_correct': False},
                ]
            },

            # Pattern & Code Reasoning
            {
                'category': Question.Category.PATTERN,
                'difficulty': Question.Difficulty.EASY,
                'order': 107,
                'prompt': 'What comes next: 3B, 6D, 9F, 12H, ___?',
                'subtitle': 'Alphanumeric Pattern (Easy)',
                'choices': [
                    {'text': '14J', 'is_correct': False},
                    {'text': '15J', 'is_correct': True, 'g': 4, 'v': 4},
                    {'text': '15I', 'is_correct': False},
                    {'text': '16J', 'is_correct': False},
                ]
            },
            {
                'category': Question.Category.PATTERN,
                'difficulty': Question.Difficulty.MEDIUM,
                'order': 108,
                'prompt': 'If TEACHER is coded as UFBDIFS (each letter shifted forward by one), how is STUDENT coded?',
                'subtitle': 'Cipher Reasoning (Medium)',
                'choices': [
                    {'text': 'TUVEOFU', 'is_correct': True, 'g': 4, 'v': 4},
                    {'text': 'TUVEOFT', 'is_correct': False},
                    {'text': 'SUVEOFU', 'is_correct': False},
                    {'text': 'TUWEOFU', 'is_correct': False},
                ]
            },
            {
                'category': Question.Category.PATTERN,
                'difficulty': Question.Difficulty.HARD,
                'order': 109,
                'prompt': 'Find the odd one out: Democracy, Monarchy, Oligarchy, Philosophy',
                'subtitle': 'Conceptual Oddity (Hard)',
                'choices': [
                    {'text': 'Democracy', 'is_correct': False},
                    {'text': 'Monarchy', 'is_correct': False},
                    {'text': 'Oligarchy', 'is_correct': False},
                    {'text': 'Philosophy', 'is_correct': True, 'g': 5, 'v': 4},
                ]
            },

            # Verbal / Logical Reasoning
            {
                'category': Question.Category.LOGIC,
                'difficulty': Question.Difficulty.EASY,
                'order': 110,
                'prompt': 'Author is to Book as Architect is to ___?',
                'subtitle': 'Logical Analogy (Easy)',
                'choices': [
                    {'text': 'Blueprint', 'is_correct': False},
                    {'text': 'Building', 'is_correct': True, 'g': 4, 'v': 4},
                    {'text': 'Construction', 'is_correct': False},
                    {'text': 'City', 'is_correct': False},
                ]
            },
            {
                'category': Question.Category.LOGIC,
                'difficulty': Question.Difficulty.MEDIUM,
                'order': 111,
                'prompt': 'All patented inventions must be novel. This invention is patented. What can we conclude?',
                'subtitle': 'Formal Logic (Medium)',
                'choices': [
                    {'text': 'This invention is expensive', 'is_correct': False},
                    {'text': 'This invention is novel', 'is_correct': True, 'g': 4, 'v': 3},
                    {'text': 'This invention will succeed commercially', 'is_correct': False},
                    {'text': 'No conclusion is possible', 'is_correct': False},
                ]
            },
            {
                'category': Question.Category.LOGIC,
                'difficulty': Question.Difficulty.HARD,
                'order': 112,
                'prompt': 'All successful negotiations require compromise. This negotiation involved no compromise. What can we conclude?',
                'subtitle': 'Conditional Logic (Hard)',
                'choices': [
                    {'text': 'This negotiation took a long time', 'is_correct': False},
                    {'text': 'This negotiation was not successful', 'is_correct': True, 'g': 5, 'v': 4},
                    {'text': 'This negotiation was successful', 'is_correct': False},
                    {'text': 'No conclusion is possible', 'is_correct': False},
                ]
            },

            # Learning Style Probes (VARK)
            {
                'category': Question.Category.VARK,
                'difficulty': Question.Difficulty.GENERAL,
                'order': 113,
                'prompt': 'When tackling a new topic in a course, I learn fastest by:',
                'subtitle': 'UG Learning Modality Probe 1',
                'choices': [
                    {'text': 'Watching a diagram-heavy or visual explanation', 'v': 5, 'a': 1, 'k': 2, 'g': 3},
                    {'text': 'Reading the material closely', 'v': 3, 'a': 4, 'k': 1, 'g': 3},
                    {'text': 'Doing the practice work immediately', 'v': 1, 'a': 1, 'k': 5, 'g': 4},
                    {'text': 'Understanding the theory or rationale before applying it', 'v': 3, 'a': 2, 'k': 2, 'g': 5},
                ]
            },
            {
                'category': Question.Category.VARK,
                'difficulty': Question.Difficulty.GENERAL,
                'order': 114,
                'prompt': 'For a group assignment, I contribute best by:',
                'subtitle': 'UG Learning Modality Probe 2',
                'choices': [
                    {'text': 'Building visuals or slides', 'v': 5, 'a': 1, 'k': 2, 'g': 3},
                    {'text': 'Writing up the analysis', 'v': 3, 'a': 4, 'k': 2, 'g': 3},
                    {'text': 'Prototyping or doing the hands-on work', 'v': 1, 'a': 1, 'k': 5, 'g': 4},
                    {'text': 'Framing the argument or strategy', 'v': 3, 'a': 3, 'k': 2, 'g': 5},
                ]
            },
            {
                'category': Question.Category.VARK,
                'difficulty': Question.Difficulty.GENERAL,
                'order': 115,
                'prompt': 'When I revisit old material to refresh it, I prefer to:',
                'subtitle': 'UG Learning Modality Probe 3',
                'choices': [
                    {'text': 'Skim diagrams or summaries', 'v': 5, 'a': 1, 'k': 2, 'g': 3},
                    {'text': 'Re-read my notes in full', 'v': 3, 'a': 4, 'k': 1, 'g': 3},
                    {'text': 'Re-do a few practice exercises', 'v': 1, 'a': 1, 'k': 5, 'g': 4},
                    {'text': 'Reconstruct the reasoning from first principles', 'v': 3, 'a': 2, 'k': 2, 'g': 5},
                ]
            },
        ]

        # ------------------- POSTGRADUATE TIER (PG) -------------------
        pg_adaptive = [
            # Reading Comprehension
            {
                'category': Question.Category.READING,
                'difficulty': Question.Difficulty.EASY,
                'order': 101,
                'prompt': '“A manager delegates a high-visibility project to a junior employee instead of a senior one, citing the junior’s fresh perspective.” What does this best illustrate?',
                'subtitle': 'Reading Comprehension (Easy)',
                'choices': [
                    {'text': 'The manager doesn’t trust senior staff', 'is_correct': False},
                    {'text': 'A deliberate choice prioritizing a specific strength over seniority', 'is_correct': True, 'g': 4, 'v': 3},
                    {'text': 'The senior employee was unavailable', 'is_correct': False},
                    {'text': 'Junior employees are always better', 'is_correct': False},
                ]
            },
            {
                'category': Question.Category.READING,
                'difficulty': Question.Difficulty.MEDIUM,
                'order': 102,
                'prompt': '“A peer-reviewed paper is retracted after other labs fail to replicate its central finding.” What does this best demonstrate?',
                'subtitle': 'Reading Comprehension (Medium)',
                'choices': [
                    {'text': 'Peer review is worthless', 'is_correct': False},
                    {'text': 'The scientific process self-correcting through replication', 'is_correct': True, 'g': 5, 'v': 4},
                    {'text': 'The original researchers committed fraud', 'is_correct': False},
                    {'text': 'Retraction means the topic was unimportant', 'is_correct': False},
                ]
            },
            {
                'category': Question.Category.READING,
                'difficulty': Question.Difficulty.HARD,
                'order': 103,
                'prompt': '“An organization adopts a policy shown to work well in one country, without adapting it to local context, and it fails there.” What principle does this best illustrate?',
                'subtitle': 'Reading Comprehension (Hard)',
                'choices': [
                    {'text': 'Best practices always transfer directly', 'is_correct': False},
                    {'text': 'Context matters when transferring solutions across settings', 'is_correct': True, 'g': 5, 'v': 4},
                    {'text': 'Policies never work anywhere', 'is_correct': False},
                    {'text': 'Failure means the original policy was flawed', 'is_correct': False},
                ]
            },

            # General Awareness
            {
                'category': Question.Category.AWARENESS,
                'difficulty': Question.Difficulty.EASY,
                'order': 104,
                'prompt': 'In project management, “scope creep” refers to:',
                'subtitle': 'General Awareness (Easy)',
                'choices': [
                    {'text': 'Reducing a project’s budget', 'is_correct': False},
                    {'text': 'Uncontrolled expansion of a project’s requirements over time', 'is_correct': True, 'g': 4, 'v': 3},
                    {'text': 'Finishing a project early', 'is_correct': False},
                    {'text': 'A type of software bug', 'is_correct': False},
                ]
            },
            {
                'category': Question.Category.AWARENESS,
                'difficulty': Question.Difficulty.MEDIUM,
                'order': 105,
                'prompt': 'A firm’s decision to prioritize short-term shareholder returns over long-term R&D investment illustrates a tradeoff between:',
                'subtitle': 'General Awareness (Medium)',
                'choices': [
                    {'text': 'Legal and illegal practices', 'is_correct': False},
                    {'text': 'Short-term gains and long-term sustainability', 'is_correct': True, 'g': 4, 'v': 4},
                    {'text': 'Marketing and HR', 'is_correct': False},
                    {'text': 'Domestic and international policy', 'is_correct': False},
                ]
            },
            {
                'category': Question.Category.AWARENESS,
                'difficulty': Question.Difficulty.HARD,
                'order': 106,
                'prompt': 'Two departments both claim ownership of a shrinking budget. Which approach is most likely to resolve this constructively?',
                'subtitle': 'General Awareness (Hard)',
                'choices': [
                    {'text': 'Ignoring the conflict', 'is_correct': False},
                    {'text': 'A structured negotiation based on shared organizational priorities', 'is_correct': True, 'g': 5, 'a': 4},
                    {'text': 'Letting the more senior department win by default', 'is_correct': False},
                    {'text': 'Escalating publicly to force a decision', 'is_correct': False},
                ]
            },

            # Pattern & Code Reasoning
            {
                'category': Question.Category.PATTERN,
                'difficulty': Question.Difficulty.EASY,
                'order': 107,
                'prompt': 'What comes next: 3D, 6H, 9L, 12P, ___?',
                'subtitle': 'Alphanumeric Series (Easy)',
                'choices': [
                    {'text': '15S', 'is_correct': False},
                    {'text': '15T', 'is_correct': True, 'g': 4, 'v': 4},
                    {'text': '14T', 'is_correct': False},
                    {'text': '16T', 'is_correct': False},
                ]
            },
            {
                'category': Question.Category.PATTERN,
                'difficulty': Question.Difficulty.MEDIUM,
                'order': 108,
                'prompt': 'If ANALYSIS is coded as BOBMZTJT (each letter shifted forward by one), how is SYNTHESIS coded?',
                'subtitle': 'Cipher Series (Medium)',
                'choices': [
                    {'text': 'TZOUIFTJT', 'is_correct': True, 'g': 4, 'v': 4},
                    {'text': 'TZOUIFSJT', 'is_correct': False},
                    {'text': 'TZOUHFTJT', 'is_correct': False},
                    {'text': 'SZOUIFTJT', 'is_correct': False},
                ]
            },
            {
                'category': Question.Category.PATTERN,
                'difficulty': Question.Difficulty.HARD,
                'order': 109,
                'prompt': 'Find the odd one out: Correlation, Causation, Regression, Symphony',
                'subtitle': 'Domain Oddity (Hard)',
                'choices': [
                    {'text': 'Correlation', 'is_correct': False},
                    {'text': 'Causation', 'is_correct': False},
                    {'text': 'Regression', 'is_correct': False},
                    {'text': 'Symphony', 'is_correct': True, 'g': 5, 'v': 4},
                ]
            },

            # Verbal / Logical Reasoning
            {
                'category': Question.Category.LOGIC,
                'difficulty': Question.Difficulty.EASY,
                'order': 110,
                'prompt': 'Hypothesis is to Experiment as Theory is to ___?',
                'subtitle': 'Epistemic Analogy (Easy)',
                'choices': [
                    {'text': 'Evidence', 'is_correct': True, 'g': 4, 'v': 4},
                    {'text': 'Guess', 'is_correct': False},
                    {'text': 'Question', 'is_correct': False},
                    {'text': 'Fiction', 'is_correct': False},
                ]
            },
            {
                'category': Question.Category.LOGIC,
                'difficulty': Question.Difficulty.MEDIUM,
                'order': 111,
                'prompt': 'All peer-reviewed studies undergo external review. This study is peer-reviewed. What can we conclude?',
                'subtitle': 'Formal Logic (Medium)',
                'choices': [
                    {'text': 'This study is definitely correct', 'is_correct': False},
                    {'text': 'This study underwent external review', 'is_correct': True, 'g': 4, 'v': 4},
                    {'text': 'This study is widely cited', 'is_correct': False},
                    {'text': 'No conclusion is possible', 'is_correct': False},
                ]
            },
            {
                'category': Question.Category.LOGIC,
                'difficulty': Question.Difficulty.HARD,
                'order': 112,
                'prompt': 'Every valid scientific theory must be falsifiable. Theory X cannot be falsified by any conceivable experiment. What can we conclude about Theory X?',
                'subtitle': 'Falsifiability Logic (Hard)',
                'choices': [
                    {'text': 'Theory X is definitely false', 'is_correct': False},
                    {'text': 'Theory X is not a valid scientific theory', 'is_correct': True, 'g': 5, 'v': 5},
                    {'text': 'Theory X is unimportant', 'is_correct': False},
                    {'text': 'No conclusion is possible', 'is_correct': False},
                ]
            },

            # Learning Style Probes (VARK)
            {
                'category': Question.Category.VARK,
                'difficulty': Question.Difficulty.GENERAL,
                'order': 113,
                'prompt': 'When engaging with a new theoretical framework, I absorb it fastest by:',
                'subtitle': 'PG Learning Modality Probe 1',
                'choices': [
                    {'text': 'Mapping it visually (diagram or model)', 'v': 5, 'a': 1, 'k': 2, 'g': 4},
                    {'text': 'Reading the original source material closely', 'v': 3, 'a': 4, 'k': 1, 'g': 4},
                    {'text': 'Applying it to a live case or dataset immediately', 'v': 2, 'a': 1, 'k': 5, 'g': 4},
                    {'text': 'Interrogating its assumptions and limits first', 'v': 3, 'a': 3, 'k': 2, 'g': 5},
                ]
            },
            {
                'category': Question.Category.VARK,
                'difficulty': Question.Difficulty.GENERAL,
                'order': 114,
                'prompt': 'In a research or project team, I add the most value by:',
                'subtitle': 'PG Learning Modality Probe 2',
                'choices': [
                    {'text': 'Building visual models or dashboards', 'v': 5, 'a': 1, 'k': 2, 'g': 4},
                    {'text': 'Writing the analysis or report', 'v': 3, 'a': 4, 'k': 2, 'g': 4},
                    {'text': 'Running the experiments or analysis hands-on', 'v': 1, 'a': 1, 'k': 5, 'g': 4},
                    {'text': 'Framing the research question and critique', 'v': 3, 'a': 3, 'k': 2, 'g': 5},
                ]
            },
            {
                'category': Question.Category.VARK,
                'difficulty': Question.Difficulty.GENERAL,
                'order': 115,
                'prompt': 'When preparing to present findings, I prepare best by:',
                'subtitle': 'PG Learning Modality Probe 3',
                'choices': [
                    {'text': 'Building charts or visuals first', 'v': 5, 'a': 1, 'k': 2, 'g': 4},
                    {'text': 'Writing a full script or narrative', 'v': 3, 'a': 5, 'k': 1, 'g': 4},
                    {'text': 'Rehearsing with the actual data live', 'v': 2, 'a': 1, 'k': 5, 'g': 4},
                    {'text': 'Thinking through likely counter-arguments first', 'v': 3, 'a': 3, 'k': 2, 'g': 5},
                ]
            },
        ]

        # Seed Part 1 adaptive tests
        tier_data_map = [
            (User.AcademicTier.SCHOOL, school_adaptive),
            (User.AcademicTier.UG, ug_adaptive),
            (User.AcademicTier.PG, pg_adaptive),
        ]

        for tier, questions_list in tier_data_map:
            for q_data in questions_list:
                q = Question.objects.create(
                    tier=tier,
                    section=Question.Section.PART_1,
                    category=q_data['category'],
                    difficulty=q_data.get('difficulty', Question.Difficulty.GENERAL),
                    order=q_data['order'],
                    prompt=q_data['prompt'],
                    subtitle=q_data.get('subtitle', ''),
                    is_active=True
                )
                for idx, c_data in enumerate(q_data['choices'], start=1):
                    Choice.objects.create(
                        question=q,
                        text=c_data['text'],
                        order=idx,
                        is_correct=c_data.get('is_correct', False),
                        tag=c_data.get('tag', ''),
                        visual_weight=c_data.get('v', 0),
                        auditory_weight=c_data.get('a', 0),
                        kinesthetic_weight=c_data.get('k', 0),
                        growth_weight=c_data.get('g', 0),
                        stress_weight=c_data.get('s', 0)
                    )

        total_q = Question.objects.count()
        total_c = Choice.objects.count()
        self.stdout.write(self.style.SUCCESS(
            f"Successfully seeded complete Adaptive Screening Test and Whole-Student Profile! ({total_q} questions, {total_c} choices)"
        ))

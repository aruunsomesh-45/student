"""
Psychometric Scoring Engine & Insights Generator
Pure Python service for calculating VARK modalities, Mindset Index,
Cognitive Aptitude accuracy, Whole-Student Profiles, and Tier-Customized Guidance.
"""

from collections import Counter
from .models import Submission, SubmissionAnswer, Choice, Question
from apps.accounts.models import User

# Comprehensive Persona Catalog
PERSONA_REGISTRY = {
    'visual_strategist': {
        'title': 'The Visual Strategist',
        'tagline': 'Master of structural mind-maps, diagrams, and visual mental modeling.',
        'icon': '🎨',
        'summary': (
            'You possess exceptional spatial and visual synthesis skills. You absorb complex systems fastest '
            'when they are translated into color-coded architectures, flowcharts, and clear conceptual frameworks. '
            'Under pressure, visual structure anchors your recall.'
        ),
        'base_motivation': 'Provide comprehensive rubrics, structural system maps, and visual progress trackers.',
        'base_comm': 'Use annotated feedback on submissions, visual diagrams, and written summaries. Avoid audio-only instructions.',
        'base_caution': 'Can experience cognitive fatigue during long, monotonous verbal-only lectures without visual materials.'
    },
    'hands_on_innovator': {
        'title': 'The Hands-On Innovator',
        'tagline': 'Learns best by building, prototyping, and experiential trial-and-error.',
        'icon': '🛠️',
        'summary': (
            'You learn with your hands and intuition. Theoretical principles click for you when you can test them '
            'in sandbox environments, write executable code, run laboratory experiments, or solve applied case studies directly.'
        ),
        'base_motivation': 'Assign practical projects, lab experiments, simulation exercises, and real-world case studies.',
        'base_comm': 'Engage through interactive whiteboard problem-solving, rapid prototyping reviews, and actionable constructive critiques.',
        'base_caution': 'Quickly loses focus and engagement during static theoretical lectures lacking practical demonstration.'
    },
    'socratic_collaborator': {
        'title': 'The Socratic Collaborator',
        'tagline': 'Thrives in debate, verbal articulation, and collaborative dialogue.',
        'icon': '🗣️',
        'summary': (
            'You synthesize information through vocal expression and dialogue. Discussing concepts out loud, '
            'teaching peers, and participating in seminars cements ideas in your mind far more effectively than silent isolated study.'
        ),
        'base_motivation': 'Provide opportunities to lead seminars, present findings to peers, and participate in academic debates.',
        'base_comm': 'Opt for 1-on-1 verbal check-ins and conversational feedback. Allow them to explain their reasoning aloud.',
        'base_caution': 'Can feel isolated and uninspired when forced into prolonged, solitary study without interactive channels.'
    },
    'analytical_synthesizer': {
        'title': 'The Analytical Synthesizer',
        'tagline': 'Driven by deep logic, first-principles reasoning, and resilient curiosity.',
        'icon': '⚡',
        'summary': (
            'You demonstrate high growth mindset stamina and methodical problem breakdown. You view difficult '
            'setbacks as data points, persevering through complex puzzles with structured deduction.'
        ),
        'base_motivation': 'Challenge with open-ended research questions, multi-variable optimization problems, and autonomous goals.',
        'base_comm': 'Provide direct, mathematically rigorous, logical feedback. Treat them as junior intellectual colleagues.',
        'base_caution': 'High self-reliance may lead them to silently struggle through blockers rather than asking for timely mentorship.'
    },
    'resilient_deep_thinker': {
        'title': 'The Resilient Deep-Thinker',
        'tagline': 'High academic stamina, reflective problem breakdown, and balanced calm under pressure.',
        'icon': '🧠',
        'summary': (
            'You possess balanced multi-modal learning instincts and robust stress regulation. You adapt '
            'seamlessly between visual models, hands-on testing, and deep conceptual reading while maintaining composure under deadline pressure.'
        ),
        'base_motivation': 'Encourage leadership in interdisciplinary projects and peer mentoring for high-stress classmates.',
        'base_comm': 'Regular strategic alignment meetings with clear milestone reviews and open-ended exploratory discussions.',
        'base_caution': 'May quietly shoulder excessive team workload during group assignments to prevent project delays.'
    }
}


def compute_psychometric_scores(choices):
    """
    Computes normalized psychometric percentage scores (0 to 100) from a collection of Choice instances.
    Formula: Score = min(100, round((Sum of Weights / (NumChoices * 5)) * 100))
    """
    if not choices:
        return {
            'visual_score': 0,
            'auditory_score': 0,
            'kinesthetic_score': 0,
            'growth_score': 0,
            'stress_score': 0,
        }

    count = len(choices)
    max_possible_weight = max(count * 5, 1)

    v_sum = sum(c.visual_weight for c in choices)
    a_sum = sum(c.auditory_weight for c in choices)
    k_sum = sum(c.kinesthetic_weight for c in choices)
    g_sum = sum(c.growth_weight for c in choices)
    s_sum = sum(c.stress_weight for c in choices)

    return {
        'visual_score': min(100, round((v_sum / max_possible_weight) * 100)),
        'auditory_score': min(100, round((a_sum / max_possible_weight) * 100)),
        'kinesthetic_score': min(100, round((k_sum / max_possible_weight) * 100)),
        'growth_score': min(100, round((g_sum / max_possible_weight) * 100)),
        'stress_score': min(100, round((s_sum / max_possible_weight) * 100)),
    }


def determine_persona(scores):
    """
    Determines the dominant learning persona using psychometric score heuristics.
    """
    v = scores.get('visual_score', 0)
    a = scores.get('auditory_score', 0)
    k = scores.get('kinesthetic_score', 0)
    g = scores.get('growth_score', 0)
    s = scores.get('stress_score', 0)

    # 1. Balanced + High Growth + Controlled Stress
    if g >= 65 and s <= 45 and abs(v - k) <= 25 and abs(v - a) <= 25:
        return PERSONA_REGISTRY['resilient_deep_thinker']

    # 2. Dominant Kinesthetic
    if k > v and k > a:
        return PERSONA_REGISTRY['hands_on_innovator']

    # 3. Dominant Visual
    if v > k and v > a:
        return PERSONA_REGISTRY['visual_strategist']

    # 4. Dominant Auditory
    if a > v and a > k:
        return PERSONA_REGISTRY['socratic_collaborator']

    # 5. Default to Analytical Synthesizer
    return PERSONA_REGISTRY['analytical_synthesizer']


def generate_student_strategies(scores, persona, tier):
    """
    Generates level-appropriate, customized study strategies for the student.
    Returns a list of tactical study advice dicts.
    """
    v = scores.get('visual_score', 0)
    a = scores.get('auditory_score', 0)
    k = scores.get('kinesthetic_score', 0)
    s = scores.get('stress_score', 0)

    strategies = []

    # Strategy 1: Core Modality Technique
    if k >= v and k >= a:
        if tier == User.AcademicTier.SCHOOL:
            strategies.append({
                'title': 'Active Problem Practice & Flashcard Sprints',
                'description': 'Solve textbook exercises on physical paper immediately after reading a concept to lock in procedural memory.',
                'tag': 'Hands-On Study'
            })
        elif tier == User.AcademicTier.UG:
            strategies.append({
                'title': 'Sandbox Prototyping & Live Code Labs',
                'description': 'Build minimal proof-of-concept scripts and lab test cases to internalize abstract theoretical algorithms.',
                'tag': 'Applied Engineering'
            })
        else: # PG
            strategies.append({
                'title': 'Empirical Experimentation & Pilot Modeling',
                'description': 'Construct exploratory sandbox datasets and pilot simulation scripts to validate research hypotheses early.',
                'tag': 'Research Prototyping'
            })
    elif v >= a:
        if tier == User.AcademicTier.SCHOOL:
            strategies.append({
                'title': 'Color-Coded Mind Maps & Diagram Walkthroughs',
                'description': 'Condense dense exam chapters into single-page visual sheets with colored highlighters and hierarchical arrows.',
                'tag': 'Visual Organization'
            })
        elif tier == User.AcademicTier.UG:
            strategies.append({
                'title': 'System Architecture Schemas & Cheat Sheets',
                'description': 'Map out software components, data flows, and mathematical matrices on a whiteboard before semester finals.',
                'tag': 'System Modeling'
            })
        else: # PG
            strategies.append({
                'title': 'Citation Graphs & Methodological Taxonomy Maps',
                'description': 'Organize literature reviews using visual citation network graphs and cross-comparative methodology tables.',
                'tag': 'Literature Synthesis'
            })
    else: # Auditory
        if tier == User.AcademicTier.SCHOOL:
            strategies.append({
                'title': 'The Feynman Explanation Method',
                'description': 'Recite tricky definitions out loud and explain concepts to a study partner or family member in simple terms.',
                'tag': 'Verbal Recall'
            })
        elif tier == User.AcademicTier.UG:
            strategies.append({
                'title': 'Peer Discussion Cohorts & Audio Lecture Reviews',
                'description': 'Host weekly peer syncs to debate challenging problem sets and listen back to key lecture segments at 1.25x speed.',
                'tag': 'Collaborative Debate'
            })
        else: # PG
            strategies.append({
                'title': 'Mock Defense Colloquiums & Academic Podcasts',
                'description': 'Simulate rigorous dissertation defense Q&A sessions with colleagues to sharpen scholarly rhetoric.',
                'tag': 'Scholarly Rhetoric'
            })

    # Strategy 2: Time & Focus Regulation
    if tier == User.AcademicTier.SCHOOL:
        strategies.append({
            'title': '25-Minute Pomodoro Intervals',
            'description': 'Break study blocks into 25 minutes of high-intensity focus followed by a 5-minute break away from screens.',
            'tag': 'Focus Stamina'
        })
    elif tier == User.AcademicTier.UG:
        strategies.append({
            'title': 'Agile Sprint Planning for Project Deadlines',
            'description': 'Triage course assignments into weekly deliverables with visible milestone checklists to avoid last-minute crunches.',
            'tag': 'Project Management'
        })
    else: # PG
        strategies.append({
            'title': 'Deep-Work Writing Boundaries',
            'description': 'Protect uninterrupted 3-hour morning deep-work blocks strictly dedicated to thesis manuscript draft production.',
            'tag': 'Writing Cadence'
        })

    # Strategy 3: Stress Management & Performance Calibration
    if s >= 60:
        strategies.append({
            'title': 'Pre-Exam Anxiety Buffer & Triage',
            'description': 'Halt intense cramming 12 hours prior to major assessments; review only 1-page high-level summaries to preserve mental energy.',
            'tag': 'Stress Buffer'
        })
    else:
        strategies.append({
            'title': 'Self-Challenge Simulation Testing',
            'description': 'Take past exam papers under strict 10% reduced time limits to condition effortless speed and calm mastery.',
            'tag': 'Performance Conditioning'
        })

    return strategies


def generate_teacher_playbook(scores, persona, wellbeing_flag='Green'):
    """
    Generates a structured 3-Pillar guidance guide for teachers and academic mentors.
    """
    stress_score = scores.get('stress_score', 0)
    growth_score = scores.get('growth_score', 0)

    # Pillar 1: Motivation Cues
    motivation = persona.get('base_motivation', 'Provide clear milestones and practical contexts.')
    if growth_score >= 70:
        motivation += ' Highly receptive to stretch goals and challenging, open-ended assignments.'
    elif growth_score <= 40:
        motivation += ' Break large tasks into low-stakes scaffolded milestones to build confidence gradually.'

    # Pillar 2: Communication & Feedback Style
    communication = persona.get('base_comm', 'Provide balanced written and verbal feedback.')

    # Pillar 3: Caution & Watchlist Triggers
    caution = persona.get('base_caution', 'Monitor during rapid lecture pacing.')
    if stress_score >= 65 or wellbeing_flag == 'Red':
        caution += ' ⚠️ [HIGH STRESS WATCHLIST]: Shows heightened vulnerability to deadline stacking and evaluation anxiety. Offer advance notice for assessments and check in 1-on-1.'
    elif stress_score <= 35:
        caution += ' Maintains exceptional composure during high-stakes exams and presentations.'

    return {
        'motivation': motivation,
        'communication': communication,
        'caution': caution,
        'is_stress_alert': stress_score >= 65 or wellbeing_flag == 'Red',
    }


def calculate_and_save_submission(user, post_data, tier=None):
    """
    Coordinates extraction of submitted choices, score calculation,
    Whole-Student Profile tags, persona assignment, teacher playbook generation, and database creation.
    """
    if not tier:
        tier = getattr(user, 'academic_tier', None) or User.AcademicTier.SCHOOL

    # Extract all question choices
    choice_ids = []
    question_choice_map = {}
    for key, value in post_data.items():
        if key.startswith('question_') and value.isdigit():
            try:
                q_id = int(key.replace('question_', ''))
                c_id = int(value)
                choice_ids.append(c_id)
                question_choice_map[q_id] = c_id
            except ValueError:
                continue

    selected_choices = list(Choice.objects.filter(id__in=choice_ids).select_related('question'))

    if not selected_choices:
        raise ValueError("No valid questions were answered in the submission.")

    # 1. Calculate normalized VARK & Mindset scores
    scores = compute_psychometric_scores(selected_choices)

    # 2. Calculate Cognitive Accuracy (Part 1 Questions with is_correct options)
    cognitive_choices = [c for c in selected_choices if c.question.section == Question.Section.PART_1 and c.question.choices.filter(is_correct=True).exists()]
    if cognitive_choices:
        correct_count = sum(1 for c in cognitive_choices if c.is_correct)
        cognitive_score = round((correct_count / len(cognitive_choices)) * 100)
    else:
        cognitive_score = 0

    # 3. Extract Whole-Student Profile Tags (Part 2)
    personality_tags = [c.tag for c in selected_choices if c.question.category == Question.Category.PERSONALITY and c.tag]
    personality_tag = Counter(personality_tags).most_common(1)[0][0] if personality_tags else 'Achiever'

    interests_tags = [c.tag for c in selected_choices if c.question.category == Question.Category.INTERESTS and c.tag]
    interests_tag = Counter(interests_tags).most_common(1)[0][0] if interests_tags else 'STEM/Analytical'

    wellbeing_tags = [c.tag for c in selected_choices if c.question.category == Question.Category.WELLBEING and c.tag]
    red_count = wellbeing_tags.count('Red')
    amber_count = wellbeing_tags.count('Amber')
    if red_count >= 2:
        wellbeing_flag = 'Red'
    elif red_count >= 1 or amber_count >= 2:
        wellbeing_flag = 'Amber'
    else:
        wellbeing_flag = 'Green'

    soft_skills = [c.tag for c in selected_choices if c.question.category == Question.Category.SOFTSKILLS and c.tag]
    soft_skills_summary = ", ".join(soft_skills) if soft_skills else "Collaborative, Strong time-management"

    open_message = post_data.get('teacher_message', '').strip()

    # 4. Determine dominant persona
    persona = determine_persona(scores)

    # 5. Generate teacher playbook
    playbook = generate_teacher_playbook(scores, persona, wellbeing_flag=wellbeing_flag)

    # 6. Create submission record
    submission = Submission.objects.create(
        student=user,
        tier=tier,
        visual_score=scores['visual_score'],
        auditory_score=scores['auditory_score'],
        kinesthetic_score=scores['kinesthetic_score'],
        growth_score=scores['growth_score'],
        stress_score=scores['stress_score'],
        cognitive_score=cognitive_score,
        personality_tag=personality_tag,
        interests_tag=interests_tag,
        wellbeing_flag=wellbeing_flag,
        soft_skills_summary=soft_skills_summary,
        open_message_to_teacher=open_message,
        persona_title=persona['title'],
        persona_tagline=persona['tagline'],
        persona_summary=persona['summary'],
        teacher_motivation=playbook['motivation'],
        teacher_communication=playbook['communication'],
        teacher_caution=playbook['caution']
    )

    # 7. Save detailed answers
    answers_to_create = [
        SubmissionAnswer(
            submission=submission,
            question=choice.question,
            selected_choice=choice
        )
        for choice in selected_choices
    ]
    SubmissionAnswer.objects.bulk_create(answers_to_create)

    # 8. Real-time sync to Supabase
    try:
        from apps.core.supabase import get_supabase_admin_client
        supa_client = get_supabase_admin_client()
        if supa_client:
            # Sync user profile if not present
            supa_client.table('accounts_user').upsert({
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'role': user.role,
                'academic_tier': getattr(user, 'academic_tier', tier),
                'institution': getattr(user, 'institution', ''),
                'department_or_subject': getattr(user, 'department_or_subject', ''),
                'grade_or_year': getattr(user, 'grade_or_year', ''),
                'avatar_color': getattr(user, 'avatar_color', '#6366f1'),
            }).execute()

            # Sync submission
            supa_client.table('assessments_submission').upsert({
                'id': submission.id,
                'student_id': user.id,
                'tier': tier,
                'visual_score': scores['visual_score'],
                'auditory_score': scores['auditory_score'],
                'kinesthetic_score': scores['kinesthetic_score'],
                'growth_score': scores['growth_score'],
                'stress_score': scores['stress_score'],
                'cognitive_score': cognitive_score,
                'personality_tag': personality_tag,
                'interests_tag': interests_tag,
                'wellbeing_flag': wellbeing_flag,
                'soft_skills_summary': soft_skills_summary,
                'open_message_to_teacher': open_message,
                'persona_title': persona['title'],
                'persona_tagline': persona['tagline'],
                'persona_summary': persona['summary'],
                'teacher_motivation': playbook['motivation'],
                'teacher_communication': playbook['communication'],
                'teacher_caution': playbook['caution']
            }).execute()
    except Exception as e:
        print(f"Supabase sync notice: {e}")

    return submission

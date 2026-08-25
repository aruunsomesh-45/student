from django.db import models
from django.conf import settings
from apps.accounts.models import User

class Question(models.Model):
    class Section(models.TextChoices):
        PART_1 = 'PART_1', 'Part 1: Core Adaptive Screening Test'
        PART_2 = 'PART_2', 'Part 2: Whole-Student Profile (Shared)'

    class Category(models.TextChoices):
        # Part 1: Core Adaptive Screening Categories
        READING = 'READING', 'Subject Knowledge — Reading Comprehension'
        AWARENESS = 'AWARENESS', 'Subject Knowledge — General Awareness'
        PATTERN = 'PATTERN', 'Cognitive Aptitude — Pattern & Code Reasoning'
        LOGIC = 'LOGIC', 'Cognitive Aptitude — Verbal / Logical Reasoning'
        VARK = 'VARK', 'Learning Style Probes'
        
        # Part 2: Whole-Student Profile Categories
        PERSONALITY = 'PERSONALITY', 'Personality (Achiever / Explorer / Collaborator / Analyst)'
        INTERESTS = 'INTERESTS', 'Interests & Career Inclination'
        WELLBEING = 'WELLBEING', 'Wellbeing & Motivation'
        SOFTSKILLS = 'SOFTSKILLS', 'Soft Skills & Behavior'

    class Difficulty(models.TextChoices):
        EASY = 'EASY', 'Easy'
        MEDIUM = 'MEDIUM', 'Medium'
        HARD = 'HARD', 'Hard'
        GENERAL = 'GENERAL', 'General / Survey'

    section = models.CharField(
        max_length=15,
        choices=Section.choices,
        default=Section.PART_1,
        help_text='Part 1 (Adaptive Test) or Part 2 (Whole-Student Profile)'
    )
    tier = models.CharField(
        max_length=10,
        choices=User.AcademicTier.choices,
        help_text='Target qualification tier (School, UG, PG)'
    )
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.VARK,
        help_text='Psychometric or assessment category'
    )
    difficulty = models.CharField(
        max_length=10,
        choices=Difficulty.choices,
        default=Difficulty.GENERAL,
        help_text='Question difficulty level'
    )
    prompt = models.TextField(
        help_text='The question or scenario presented to the student'
    )
    subtitle = models.CharField(
        max_length=255,
        blank=True,
        help_text='Short subtitle or contextual hint'
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text='Order in which the question appears in the quiz'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Whether this question is active in quizzes'
    )

    class Meta:
        ordering = ['tier', 'section', 'order', 'id']
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'

    def __str__(self):
        return f"[{self.tier} - {self.get_category_display()}] Q{self.order}: {self.prompt[:60]}..."


class Choice(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='choices'
    )
    text = models.CharField(
        max_length=350,
        help_text='Option text presented to the student'
    )
    order = models.PositiveSmallIntegerField(
        default=0,
        help_text='Order of display among choices'
    )
    is_correct = models.BooleanField(
        default=False,
        help_text='Whether this is the correct answer (for cognitive/subject tests)'
    )
    tag = models.CharField(
        max_length=60,
        blank=True,
        help_text='Associated trait or style tag (e.g. Achiever, STEM/Analytical, Leadership-leaning)'
    )
    
    # Psychometric weight vectors (0 to 5)
    visual_weight = models.PositiveSmallIntegerField(
        default=0,
        help_text='Visual learning affinity weight (0-5)'
    )
    auditory_weight = models.PositiveSmallIntegerField(
        default=0,
        help_text='Auditory learning affinity weight (0-5)'
    )
    kinesthetic_weight = models.PositiveSmallIntegerField(
        default=0,
        help_text='Kinesthetic/hands-on learning affinity weight (0-5)'
    )
    growth_weight = models.PositiveSmallIntegerField(
        default=0,
        help_text='Growth mindset & resilience affinity weight (0-5)'
    )
    stress_weight = models.PositiveSmallIntegerField(
        default=0,
        help_text='Stress vulnerability weight (0-5)'
    )

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'Choice'
        verbose_name_plural = 'Choices'

    def __str__(self):
        return f"{self.question.prompt[:30]}... -> {self.text[:40]}"


class Submission(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='submissions'
    )
    tier = models.CharField(
        max_length=10,
        choices=User.AcademicTier.choices,
        help_text='Academic tier at the time of submission'
    )
    submitted_at = models.DateTimeField(
        auto_now_add=True
    )
    
    # Normalized calculated scores (0-100%)
    visual_score = models.IntegerField(default=0, help_text='Visual affinity percentage')
    auditory_score = models.IntegerField(default=0, help_text='Auditory affinity percentage')
    kinesthetic_score = models.IntegerField(default=0, help_text='Kinesthetic affinity percentage')
    growth_score = models.IntegerField(default=0, help_text='Growth mindset score percentage')
    stress_score = models.IntegerField(default=0, help_text='Stress response score percentage')
    cognitive_score = models.IntegerField(default=0, help_text='Cognitive/knowledge accuracy percentage')

    # Part 2: Whole-Student Profile Tags
    personality_tag = models.CharField(max_length=60, blank=True, help_text='Achiever / Explorer / Collaborator / Analyst')
    interests_tag = models.CharField(max_length=60, blank=True, help_text='STEM / Creative / People / Business')
    wellbeing_flag = models.CharField(max_length=20, default='Green', help_text='Green / Amber / Red')
    soft_skills_summary = models.CharField(max_length=255, blank=True)
    open_message_to_teacher = models.TextField(blank=True, help_text='Student open message to teacher')

    # Persona & Insights summary
    persona_title = models.CharField(max_length=120, default='Evolving Learner')
    persona_tagline = models.CharField(max_length=255, default='Developing multi-modal study instincts.')
    persona_summary = models.TextField(blank=True)
    
    # 3-Pillar Teacher Playbook Insights
    teacher_motivation = models.TextField(
        blank=True,
        help_text='How to motivate and assign tasks to this student'
    )
    teacher_communication = models.TextField(
        blank=True,
        help_text='Best feedback and communication channels'
    )
    teacher_caution = models.TextField(
        blank=True,
        help_text='Stress triggers and what to watch out for'
    )

    class Meta:
        ordering = ['-submitted_at']
        verbose_name = 'Assessment Submission'
        verbose_name_plural = 'Assessment Submissions'

    def __str__(self):
        return f"{self.student.get_full_name() or self.student.username} - {self.persona_title} ({self.submitted_at.strftime('%b %d, %Y')})"

    @property
    def dominant_modality(self):
        modalities = [
            ('Visual', self.visual_score),
            ('Auditory', self.auditory_score),
            ('Kinesthetic', self.kinesthetic_score),
        ]
        modalities.sort(key=lambda x: x[1], reverse=True)
        return modalities[0][0]

    @property
    def is_stress_alert(self):
        return self.stress_score >= 65 or self.wellbeing_flag == 'Red'


class SubmissionAnswer(models.Model):
    submission = models.ForeignKey(
        Submission,
        on_delete=models.CASCADE,
        related_name='answers'
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE
    )
    selected_choice = models.ForeignKey(
        Choice,
        on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ('submission', 'question')
        verbose_name = 'Submission Answer'
        verbose_name_plural = 'Submission Answers'

    def __str__(self):
        return f"Sub #{self.submission.id} - Q{self.question.id}"

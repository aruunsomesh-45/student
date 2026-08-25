from django.db import models
from django.conf import settings
from apps.assessments.models import Submission

class TeacherNote(models.Model):
    """
    Private observation notes and mentorship logs maintained by teachers for individual students.
    Strictly isolated and visible only to authenticated teachers.
    """
    class Category(models.TextChoices):
        OBSERVATION = 'OBSERVATION', 'General Observation'
        ACADEMIC = 'ACADEMIC', 'Academic Scaffolding'
        WELLBEING = 'WELLBEING', 'Wellbeing & Stress Support'
        INTERVENTION = 'INTERVENTION', 'Targeted Intervention'
        AI_STRATEGY = 'AI_STRATEGY', 'AI Pedagogical Plan'

    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='authored_teacher_notes',
        help_text='The educator who recorded the note'
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='teacher_notes',
        help_text='The student this note pertains to'
    )
    submission = models.ForeignKey(
        Submission,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='teacher_notes',
        help_text='Optional assessment submission linked to this observation'
    )
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.OBSERVATION,
        help_text='Note classification'
    )
    content = models.TextField(
        help_text='Private educator observation, conference log, or intervention notes'
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Teacher Observation Note'
        verbose_name_plural = 'Teacher Observation Notes'

    def __str__(self):
        return f"Note by {self.teacher.get_full_name() or self.teacher.username} on {self.student.get_full_name() or self.student.username} ({self.created_at.strftime('%b %d, %Y')})"

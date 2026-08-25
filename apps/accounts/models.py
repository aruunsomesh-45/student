from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = 'STUDENT', 'Student'
        TEACHER = 'TEACHER', 'Teacher'
        ADMIN = 'ADMIN', 'Administrator'

    class AcademicTier(models.TextChoices):
        SCHOOL = 'SCHOOL', 'Schooling (10th / 12th)'
        UG = 'UG', 'Undergraduate (UG)'
        PG = 'PG', 'Postgraduate (PG)'

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.STUDENT,
        help_text='Designates whether this user is a student, teacher, or admin.'
    )
    academic_tier = models.CharField(
        max_length=10,
        choices=AcademicTier.choices,
        null=True,
        blank=True,
        help_text='Qualification level for students to filter question sets.'
    )
    grade_or_year = models.CharField(
        max_length=50,
        blank=True,
        help_text='Specific grade or study year (e.g., 10th Grade, 12th Science, 3rd Year B.Tech).'
    )
    institution = models.CharField(
        max_length=150,
        blank=True,
        help_text='School, College, or University name.'
    )
    department_or_subject = models.CharField(
        max_length=100,
        blank=True,
        help_text='Primary department or subject taught (for teachers) or major (for students).'
    )
    avatar_color = models.CharField(
        max_length=30,
        default='#4f46e5',
        help_text='Hex or Tailwind color token for student avatar.'
    )

    def is_teacher_user(self):
        return self.role == self.Role.TEACHER or self.is_staff or self.is_superuser

    def is_student_user(self):
        return self.role == self.Role.STUDENT

    def get_tier_display_label(self):
        if self.academic_tier:
            return dict(self.AcademicTier.choices).get(self.academic_tier, self.academic_tier)
        return 'Not Specified'

    def __str__(self):
        full_name = self.get_full_name() or self.username
        return f"{full_name} ({self.get_role_display()})"

from django.apps import AppConfig
from django.db.models.signals import post_migrate

def auto_seed_questions(sender, **kwargs):
    try:
        from apps.assessments.models import Question
        if Question.objects.count() == 0:
            from django.core.management import call_command
            call_command('seed_questions')
    except Exception:
        pass

class AssessmentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.assessments'

    def ready(self):
        post_migrate.connect(auto_seed_questions, sender=self)

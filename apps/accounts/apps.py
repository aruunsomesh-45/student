from django.apps import AppConfig
from django.db.models.signals import post_migrate

def ensure_site_exists(sender, **kwargs):
    try:
        from django.contrib.sites.models import Site
        Site.objects.get_or_create(
            id=1,
            defaults={
                'domain': 'web-production-a7c4d.up.railway.app',
                'name': 'MindConnect'
            }
        )
    except Exception:
        pass

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.accounts'

    def ready(self):
        post_migrate.connect(ensure_site_exists, sender=self)

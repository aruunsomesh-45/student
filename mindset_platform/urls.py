import logging
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.conf import settings
from django.conf.urls.static import static

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Health check — used by Railway, uptime monitors
# ---------------------------------------------------------------------------
def health_check(request):
    db_status = 'ok'
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
    except Exception as e:
        db_status = f'error: {e}'
    return JsonResponse({'status': 'ok', 'database': db_status, 'debug': settings.DEBUG})


# ---------------------------------------------------------------------------
# Custom error handlers — renders 404.html / 500.html (DEBUG=False only)
# ---------------------------------------------------------------------------
handler404 = 'mindset_platform.urls.page_not_found'
handler500 = 'mindset_platform.urls.server_error'


def page_not_found(request, exception):
    from django.shortcuts import render
    return render(request, '404.html', status=404)


def server_error(request):
    import traceback, sys
    exc_type, exc_value, exc_traceback = sys.exc_info()
    if exc_type is not None:
        logger.error(
            "Unhandled 500 Exception on %s:\n%s",
            request.path,
            "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        )
    from django.shortcuts import render
    return render(request, '500.html', status=500)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health_check'),
    path('', include('apps.core.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('accounts/', include('allauth.urls')),
    path('assessments/', include('apps.assessments.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

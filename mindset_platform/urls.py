from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.conf import settings
from django.conf.urls.static import static

# ---------------------------------------------------------------------------
# Health check — used by Vercel, Railway, Render, uptime monitors
# ---------------------------------------------------------------------------
def health_check(request):
    return JsonResponse({'status': 'ok', 'debug': settings.DEBUG})


# ---------------------------------------------------------------------------
# Custom error handlers — renders 404.html / 500.html (DEBUG=False only)
# ---------------------------------------------------------------------------
handler404 = 'mindset_platform.urls.page_not_found'
handler500 = 'mindset_platform.urls.server_error'


def page_not_found(request, exception):
    from django.shortcuts import render
    return render(request, '404.html', status=404)


def server_error(request):
    from django.shortcuts import render
    return render(request, '500.html', status=500)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health_check'),   # ← health endpoint
    path('', include('apps.core.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('accounts/', include('allauth.urls')),
    path('assessments/', include('apps.assessments.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


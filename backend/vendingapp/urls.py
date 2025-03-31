from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import logging

logger = logging.getLogger(__name__)

# Simple debug view to test API connectivity
def debug_view(request):
    logger.info(f"Debug view accessed with method: {request.method}")
    logger.info(f"Headers: {dict(request.headers)}")
    return JsonResponse({
        'status': 'ok',
        'message': 'API is working',
        'method': request.method,
        'path': request.path,
        'is_secure': request.is_secure(),
        'host': request.get_host(),
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', csrf_exempt(TokenObtainPairView.as_view()), name='token_obtain_pair'),
    path('api/token/refresh/', csrf_exempt(TokenRefreshView.as_view()), name='token_refresh'),
    path('api/', include('core.urls')),
    # Debug endpoints
    path('api/debug/', csrf_exempt(debug_view), name='debug_api'),
    path('debug/', TemplateView.as_view(template_name='debug.html')),
    # Serve Vue App
    path('', TemplateView.as_view(template_name='index.html')),
]

# Add media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
# Add this catch-all route at the end to handle Vue router paths
urlpatterns += [
    path('<path:path>', TemplateView.as_view(template_name='index.html')),
] 
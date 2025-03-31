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
from django.contrib.auth import authenticate, get_user_model
from django.db import connection
import logging
import json

logger = logging.getLogger(__name__)
User = get_user_model()

# Simple debug view to test API connectivity
def debug_view(request):
    logger.info(f"Debug view accessed with method: {request.method}")
    logger.info(f"Headers: {dict(request.headers)}")
    
    # Print SQL queries for debugging
    with connection.execute_wrapper(lambda execute, sql, params, many, context: logger.info(f"SQL: {sql}")):
        # Check if specific username exists
        username = 'vicente'
        user_exists = User.objects.filter(username=username).exists()
        user_count = User.objects.count()
        
        # Get list of all usernames for debugging
        all_users = list(User.objects.values_list('username', flat=True))
        
        # Test authentication
        auth_result = None
        if request.method == 'POST':
            try:
                data = json.loads(request.body)
                test_username = data.get('username', username)
                test_password = data.get('password', '')
                
                # Test Django authentication
                user = authenticate(username=test_username, password=test_password)
                auth_result = {
                    'success': user is not None,
                    'user_id': getattr(user, 'id', None),
                    'username': getattr(user, 'username', None) if user else None,
                    'is_active': getattr(user, 'is_active', None) if user else None,
                    'is_staff': getattr(user, 'is_staff', None) if user else None,
                    'is_superuser': getattr(user, 'is_superuser', None) if user else None,
                }
            except Exception as e:
                logger.error(f"Authentication test error: {str(e)}")
                auth_result = {'error': str(e)}
    
    return JsonResponse({
        'status': 'ok',
        'message': 'API is working',
        'method': request.method,
        'path': request.path,
        'is_secure': request.is_secure(),
        'host': request.get_host(),
        'user_debug': {
            'user_exists': user_exists,
            'user_count': user_count,
            'all_users': all_users,
            'auth_result': auth_result
        }
    })

# Simple direct authentication test view
def direct_auth_view(request):
    if request.method != 'POST':
        return JsonResponse({"error": "POST method required"}, status=400)
    
    try:
        data = json.loads(request.body)
        username = data.get('username', '')
        password = data.get('password', '')
        
        logger.info(f"Testing direct auth for user: {username}")
        
        # Test direct authentication
        user = authenticate(username=username, password=password)
        
        if user is not None:
            return JsonResponse({
                "authenticated": True,
                "user_id": user.id,
                "username": user.username,
                "is_active": user.is_active,
                "is_staff": user.is_staff,
                "is_superuser": user.is_superuser
            })
        else:
            # Get detailed error info
            try:
                # Check if user exists
                user_exists = User.objects.filter(username=username).exists()
                
                # If user exists, password is likely wrong
                if user_exists:
                    user_obj = User.objects.get(username=username)
                    return JsonResponse({
                        "authenticated": False,
                        "error": "Invalid credentials",
                        "user_exists": True,
                        "user_active": user_obj.is_active,
                        "has_usable_password": user_obj.has_usable_password()
                    })
                else:
                    return JsonResponse({
                        "authenticated": False,
                        "error": "User does not exist",
                        "user_exists": False
                    })
            except Exception as e:
                logger.error(f"Error during user check: {str(e)}")
                return JsonResponse({
                    "authenticated": False,
                    "error": str(e)
                })
    except Exception as e:
        logger.error(f"Direct auth error: {str(e)}")
        return JsonResponse({"error": str(e)}, status=400)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', csrf_exempt(TokenObtainPairView.as_view()), name='token_obtain_pair'),
    path('api/token/refresh/', csrf_exempt(TokenRefreshView.as_view()), name='token_refresh'),
    path('api/', include('core.urls')),
    # Debug endpoints
    path('api/debug/', csrf_exempt(debug_view), name='debug_api'),
    path('api/direct-auth/', csrf_exempt(direct_auth_view), name='direct_auth'),
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
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
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import authenticate, get_user_model
from django.db import connection
import logging
import json
from django.core.management import call_command
from io import StringIO
import os

logger = logging.getLogger(__name__)
User = get_user_model()

# Database table check function
def check_database_tables(connection):
    db_tables = {}
    try:
        with connection.cursor() as cursor:
            # Check database type
            db_engine = connection.vendor
            db_tables['database_type'] = db_engine
            
            if db_engine == 'sqlite':
                # SQLite specific query
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                db_tables['tables'] = [table[0] for table in tables]
                
                # Check for auth_user specifically
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='auth_user';")
                auth_user_exists = cursor.fetchone() is not None
            elif db_engine == 'postgresql':
                # PostgreSQL specific query
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    ORDER BY table_name;
                """)
                tables = cursor.fetchall()
                db_tables['tables'] = [table[0] for table in tables]
                
                # Check for auth_user specifically
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' AND table_name = 'auth_user';
                """)
                auth_user_exists = cursor.fetchone() is not None
            else:
                # Other databases - generic approach
                cursor.execute("SELECT 1 FROM auth_user LIMIT 1;")
                auth_user_exists = True
    except Exception as e:
        if 'no such table: auth_user' in str(e):
            auth_user_exists = False
        else:
            logger.error(f"DB table check error: {str(e)}")
            db_tables['error'] = str(e)
            return db_tables
    
    db_tables['auth_user_exists'] = auth_user_exists
    return db_tables

# Simple debug view to test API connectivity
def debug_view(request):
    logger.info(f"Debug view accessed with method: {request.method}")
    logger.info(f"Headers: {dict(request.headers)}")
    
    # Database table check
    db_tables = check_database_tables(connection)
    
    # Print SQL queries for debugging
    with connection.execute_wrapper(lambda execute, sql, params, many, context: logger.info(f"SQL: {sql}")):
        # Check if specific username exists
        username = 'vicente'
        user_exists = False
        user_count = 0
        all_users = []
        
        try:
            user_exists = User.objects.filter(username=username).exists()
            user_count = User.objects.count()
            all_users = list(User.objects.values_list('username', flat=True))
        except Exception as e:
            logger.error(f"User check error: {str(e)}")
        
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
        'database': db_tables,
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

# Migration view
def migrate_view(request):
    """Run migrations from the web."""
    if request.META.get('REMOTE_ADDR') not in ['127.0.0.1', 'localhost']:
        # Add extra security check - only run if a secret is provided
        if request.GET.get('secret') != settings.SECRET_KEY[:8]:
            return JsonResponse({
                'status': 'error',
                'message': 'Unauthorized'
            }, status=403)
    
    output = StringIO()
    try:
        # Run makemigrations first to ensure migration files exist
        call_command('makemigrations', stdout=output)
        output.write("\n\n--- Running migrate ---\n\n")
        # Run migrate to apply migrations
        call_command('migrate', stdout=output)
        
        # Check database status after migrations
        db_tables = check_database_tables(connection)
        
        # Create a superuser if no users exist
        user_count = 0
        superuser_created = False
        
        try:
            user_count = User.objects.count()
            if user_count == 0:
                # Create a default superuser
                output.write("\n\n--- Creating default superuser ---\n\n")
                User.objects.create_superuser(
                    username='vicente', 
                    email='admin@example.com',
                    password='186422775'
                )
                output.write("Superuser 'vicente' created successfully.\n")
                superuser_created = True
        except Exception as e:
            output.write(f"\nError checking/creating users: {str(e)}\n")
        
        return JsonResponse({
            'status': 'success',
            'message': 'Migrations applied',
            'output': output.getvalue(),
            'database': db_tables,
            'user_count': user_count,
            'superuser_created': superuser_created
        })
    except Exception as e:
        logger.error(f"Migration error: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': str(e),
            'output': output.getvalue()
        }, status=500)

# Direct debug view that cannot be intercepted by other views
def direct_debug_view(request):
    """Emergency access debug page that bypasses all routing."""
    with open(os.path.join(settings.BASE_DIR, 'backend/templates/debug.html'), 'r') as f:
        return HttpResponse(f.read())

# Direct migration view with explicit response (not JSON)
def direct_migrate_view(request):
    """Run migrations directly with HTML output."""
    # Basic security check
    secret_key = request.GET.get('key', '')
    if not settings.DEBUG and secret_key != settings.SECRET_KEY[:8]:
        return HttpResponse("<h1>Unauthorized</h1><p>Provide the correct key parameter.</p>", status=403)
    
    output = StringIO()
    try:
        output.write("Running makemigrations...\n")
        call_command('makemigrations', stdout=output)
        
        output.write("\n\nRunning migrate...\n")
        call_command('migrate', stdout=output)
        
        # Check database status
        output.write("\n\nChecking database status...\n")
        try:
            with connection.cursor() as cursor:
                if connection.vendor == 'sqlite':
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                elif connection.vendor == 'postgresql':
                    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
                tables = cursor.fetchall()
                output.write(f"Found {len(tables)} tables:\n")
                for table in tables:
                    output.write(f"- {table[0]}\n")
        except Exception as e:
            output.write(f"Error checking tables: {str(e)}\n")
        
        # Create superuser if needed
        output.write("\n\nChecking for superuser...\n")
        try:
            superuser_exists = User.objects.filter(is_superuser=True).exists()
            user_count = User.objects.count()
            output.write(f"User count: {user_count}\n")
            output.write(f"Superuser exists: {superuser_exists}\n")
            
            if not superuser_exists:
                output.write("Creating superuser 'vicente'...\n")
                User.objects.create_superuser(
                    username='vicente',
                    email='admin@example.com',
                    password='186422775'
                )
                output.write("Superuser created successfully!\n")
        except Exception as e:
            output.write(f"Error creating superuser: {str(e)}\n")
        
        result = f"""
        <html>
        <head>
            <title>Migration Results</title>
            <style>
                body {{ font-family: monospace; padding: 20px; }}
                pre {{ background: #f4f4f4; padding: 10px; border-radius: 5px; overflow: auto; }}
                .success {{ color: green; }}
            </style>
        </head>
        <body>
            <h1>Migration Complete</h1>
            <p class="success">Migrations were applied successfully!</p>
            <h2>Output:</h2>
            <pre>{output.getvalue()}</pre>
            <p><a href="/debug/">Go to Debug Page</a></p>
            <p><a href="/login">Go to Login Page</a></p>
        </body>
        </html>
        """
        return HttpResponse(result)
    except Exception as e:
        error_result = f"""
        <html>
        <head>
            <title>Migration Error</title>
            <style>
                body {{ font-family: monospace; padding: 20px; }}
                pre {{ background: #f4f4f4; padding: 10px; border-radius: 5px; overflow: auto; }}
                .error {{ color: red; }}
            </style>
        </head>
        <body>
            <h1>Migration Error</h1>
            <p class="error">Error: {str(e)}</p>
            <h2>Output before error:</h2>
            <pre>{output.getvalue()}</pre>
        </body>
        </html>
        """
        return HttpResponse(error_result, status=500)

urlpatterns = [
    path('admin/', admin.site.urls),
    # Debug endpoints - placed before Vue routing to take priority
    path('debug/', TemplateView.as_view(template_name='debug.html')),
    path('emergency-debug/', direct_debug_view, name='emergency_debug'),
    path('run-migrations/', direct_migrate_view, name='direct_migrations'),
    path('api/debug/', csrf_exempt(debug_view), name='debug_api'),
    path('api/direct-auth/', csrf_exempt(direct_auth_view), name='direct_auth'),
    path('api/run-migrations/', migrate_view, name='run_migrations'),
    # API endpoints
    path('api/token/', csrf_exempt(TokenObtainPairView.as_view()), name='token_obtain_pair'),
    path('api/token/refresh/', csrf_exempt(TokenRefreshView.as_view()), name='token_refresh'),
    path('api/', include('core.urls')),
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
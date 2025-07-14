import json
from django.utils import timezone
from .models import ActivityLog
from django.contrib.sessions.middleware import SessionMiddleware

class ActivityLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip paths yang tidak perlu dicatat
        EXCLUDED_PATHS = [
            '/admin/',
            '/static/',
            '/media/',
            '/favicon.ico',
        ]
        # Pastikan session sudah diproses
        SessionMiddleware(lambda req: None).process_request(request)
        
        # 1. Handle Tahun Periode
        if 'tahun_periode' not in request.session:
            request.session['tahun_periode'] = '2024'  # Default tahun
            
        if any(request.path.startswith(path) for path in EXCLUDED_PATHS):
            return self.get_response(request)

        response = self.get_response(request)

        try:
            

            # Deteksi aplikasi berdasarkan URL
            app_mapping = {
                '/dashboard/': 'DASHBOARD',
                '/data/': 'DATA',
                '/master/': 'MASTER',
            }
            
            current_app = 'OTHER'
            for path_prefix, app_name in app_mapping.items():
                if request.path.startswith(path_prefix):
                    current_app = app_name
                    break

            # Deteksi jenis aktivitas
            activity_type = 'VIEW'
            if request.method == 'POST':
                activity_type = 'CREATE'
            elif request.method in ['PUT', 'PATCH']:
                activity_type = 'EDIT'
            elif request.method == 'DELETE':
                activity_type = 'DELETE'
            elif request.path == '/login/':
                activity_type = 'LOGIN'
            elif request.path == '/logout/':
                activity_type = 'LOGOUT'

            # Simpan ke database
            ActivityLog.objects.create(
                user=request.user if request.user.is_authenticated else None,
                activity_type=activity_type,
                app=current_app,
                path=request.path,
                method=request.method,
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                extra_data={
                    'status_code': response.status_code,
                    'referer': request.META.get('HTTP_REFERER', ''),
                }
            )
        except Exception as e:
            # Handle error tanpa mengganggu aplikasi
            pass

        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        return x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
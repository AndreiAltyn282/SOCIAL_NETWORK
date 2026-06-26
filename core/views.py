from django.shortcuts import render
from django.http import JsonResponse

def index(request):
    """Главная страница сайта"""
    return render(request, 'core/index.html')

def api_root(request):
    """Информация об API"""
    return JsonResponse({
        'message': 'Добро пожаловать в ProSocial API',
        'version': '1.0.0',
        'endpoints': {
            'users': '/api/users/',
            'posts': '/api/posts/',
            'comments': '/api/comments/',
            'conversations': '/api/conversations/',
            'messages': '/api/messages/',
            'subscriptions': '/api/subscriptions/',
            'startup_packs': '/api/startup-packs/',
            'notifications': '/api/notifications/',
            'token': '/api/token/',
            'token_refresh': '/api/token/refresh/',
        },
        'documentation': 'Browse API at /api/',
        'admin': '/admin/'
    })

def health_check(request):
    """Проверка статуса сервера"""
    return JsonResponse({
        'status': 'ok',
        'message': 'Сервер работает!'
    })

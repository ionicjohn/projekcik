from django.http import JsonResponse

def handler404(request, exception):
    """Custom handler for 404 errors"""
    return JsonResponse({
        'success': False,
        'message': 'Endpoint not found',
        'status_code': 404
    }, status=404)

def handler500(request):
    """Custom handler for 500 errors"""
    return JsonResponse({
        'success': False,
        'message': 'Internal server error',
        'status_code': 500
    }, status=500)
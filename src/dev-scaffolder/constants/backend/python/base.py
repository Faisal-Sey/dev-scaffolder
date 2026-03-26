DJANGO_APP_URL_CONFIG = (
    f"from django.urls import path\n"
    f"from views import hello\n\n"
    f"urlpatterns = [\n"
    f"    path('', hello, name='hello'),\n"
    f"]\n"
)

DJANGO_VIEW_FUNCTION_IMPORT_JSON_RESPONSE = "from django.http import JsonResponse\n\n"

DJANGO_VIEW_FUNCTION_MESSAGE = '{"success": True, "message": "hello"}'

DJANGO_VIEW_FUNCTION = (
    f"def hello() -> JsonResponse:\n"
    f"  return JsonResponse({DJANGO_VIEW_FUNCTION_MESSAGE})"
)
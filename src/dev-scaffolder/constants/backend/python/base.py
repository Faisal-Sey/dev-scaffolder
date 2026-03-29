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

DJANGO_DRF_SETTINGS = (
    "\n\nREST_FRAMEWORK = {\n"
    "    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',\n"
    "    'PAGE_SIZE': 10,\n"
    "}\n"
)

DJANGO_DRF_SERIALIZER = (
    "from rest_framework import serializers\n\n\n"
    "class HelloSerializer(serializers.Serializer):\n"
    "    message = serializers.CharField(max_length=200)\n"
)

DJANGO_DRF_VIEW = (
    "from rest_framework.views import APIView\n"
    "from rest_framework.response import Response\n"
    "from rest_framework import status\n"
    "from .serializers import HelloSerializer\n\n\n"
    "class HelloView(APIView):\n"
    "    def get(self, request):\n"
    "        data = {'message': 'hello'}\n"
    "        serializer = HelloSerializer(data)\n"
    "        return Response(serializer.data, status=status.HTTP_200_OK)\n"
)

DJANGO_DRF_URL_CONFIG = (
    "from django.urls import path\n"
    "from .views import HelloView\n\n"
    "urlpatterns = [\n"
    "    path('', HelloView.as_view(), name='hello'),\n"
    "]\n"
)

DJANGO_POSTGRESQL_DATABASES = (
    "DATABASES = {\n"
    "    'default': {\n"
    "        'ENGINE': 'django.db.backends.postgresql',\n"
    "        'NAME': os.environ.get('DB_NAME', 'mydb'),\n"
    "        'USER': os.environ.get('DB_USER', 'postgres'),\n"
    "        'PASSWORD': os.environ.get('DB_PASSWORD', ''),\n"
    "        'HOST': os.environ.get('DB_HOST', 'localhost'),\n"
    "        'PORT': os.environ.get('DB_PORT', '5432'),\n"
    "    }\n"
    "}\n"
)

DJANGO_POSTGRESQL_ENV_EXAMPLE = (
    "DB_NAME=mydb\n"
    "DB_USER=postgres\n"
    "DB_PASSWORD=\n"
    "DB_HOST=localhost\n"
    "DB_PORT=5432\n"
)

DJANGO_CORS_SETTINGS = (
    "\n\n# django-cors-headers configuration\n"
    "CORS_ALLOW_CREDENTIALS = False\n"
    "CORS_ALLOWED_ORIGINS = [\n"
    "   'https://example.com',\n"
    "   'http://localhost:3000',\n"
    "]\n"
)
from .cors_headers import CorsHeadersBattery
from .rest_framework import RestFrameworkBattery
from .postgresql import PostgreSQLBattery
from .python_dotenv import PythonDotenvBattery
from .django_environ import DjangoEnvironBattery
from .whitenoise import WhitenoiseBattery
from .celery import CeleryBattery

__all__ = [
    'CorsHeadersBattery',
    'RestFrameworkBattery',
    'PostgreSQLBattery',
    'PythonDotenvBattery',
    'DjangoEnvironBattery',
    'WhitenoiseBattery',
    'CeleryBattery',
]

from typing import List

from batteries.base import BaseBattery
from batteries.django import (
    CorsHeadersBattery,
    RestFrameworkBattery,
    PostgreSQLBattery,
    PythonDotenvBattery,
    DjangoEnvironBattery,
    WhitenoiseBattery,
    CeleryBattery,
    GitHubActionsBattery,
    GitLabCIBattery,
    BitbucketPipelinesBattery,
    CircleCIBattery,
    PytestBattery,
    UnitTestBattery,
    CoverageBattery,
    FactoryBoyBattery,
    LoggingMonitoringBattery,
    SentryBattery,
    StructlogBattery,
)
from batteries.fastapi import (
    FastAPICORSBattery,
    FastAPISQLAlchemyBattery,
    FastAPITortoiseORMBattery,
    FastAPICeleryBattery,
    FastAPIPytestBattery,
    FastAPISentryBattery,
    FastAPIStructlogBattery,
)

# Single source of truth for available batteries.
# Add new batteries here; all executors that use parse_batteries() pick them up automatically.
BATTERY_MAP = {
    # Dependencies
    'rest framework': RestFrameworkBattery,
    'cors headers': CorsHeadersBattery,
    'postgresql': PostgreSQLBattery,
    'python dotenv': PythonDotenvBattery,
    'django environ': DjangoEnvironBattery,
    'whitenoise': WhitenoiseBattery,
    'celery': CeleryBattery,
    # CI/CD
    'github actions': GitHubActionsBattery,
    'gitlab ci': GitLabCIBattery,
    'bitbucket pipelines': BitbucketPipelinesBattery,
    'circleci': CircleCIBattery,
    # Testing
    'pytest': PytestBattery,
    'unittest': UnitTestBattery,
    'coverage': CoverageBattery,
    'factory boy': FactoryBoyBattery,
    # Logging / Monitoring
    'logging': LoggingMonitoringBattery,
    'sentry': SentryBattery,
    'structlog': StructlogBattery,
}


FASTAPI_BATTERY_MAP = {
    # Middleware
    'cors': FastAPICORSBattery,
    # Databases
    'sqlalchemy': FastAPISQLAlchemyBattery,
    'tortoise orm': FastAPITortoiseORMBattery,
    # Background Tasks
    'celery': FastAPICeleryBattery,
    # Testing
    'pytest': FastAPIPytestBattery,
    # Logging / Monitoring
    'sentry': FastAPISentryBattery,
    'structlog': FastAPIStructlogBattery,
}


def parse_batteries(batteries_str: str) -> List[BaseBattery]:
    """
    Parse a comma-separated battery string into instantiated battery objects.

    :param batteries_str: Comma-separated battery names, e.g. "Rest Framework,PostgreSQL"
    :return: List of instantiated battery objects.
    """
    return [
        BATTERY_MAP[name.strip().lower()]()
        for name in batteries_str.split(',')
        if name.strip().lower() in BATTERY_MAP
    ]


def parse_fastapi_batteries(batteries_str: str) -> List[BaseBattery]:
    """
    Parse a comma-separated battery string into instantiated FastAPI battery objects.

    :param batteries_str: Comma-separated battery names, e.g. "CORS,SQLAlchemy"
    :return: List of instantiated battery objects.
    """
    return [
        FASTAPI_BATTERY_MAP[name.strip().lower()]()
        for name in batteries_str.split(',')
        if name.strip().lower() in FASTAPI_BATTERY_MAP
    ]

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

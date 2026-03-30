from typing import List

from batteries.base import BaseBattery
from batteries.django import (
    CorsHeadersBattery,
    RestFrameworkBattery,
    PostgreSQLBattery,
    PythonDotenvBattery,
    DjangoEnvironBattery,
    WhitenoiseBattery,
)

# Single source of truth for available batteries.
# Add new batteries here; all executors that use parse_batteries() pick them up automatically.
BATTERY_MAP = {
    'rest framework': RestFrameworkBattery,
    'cors headers': CorsHeadersBattery,
    'postgresql': PostgreSQLBattery,
    'python dotenv': PythonDotenvBattery,
    'django environ': DjangoEnvironBattery,
    'whitenoise': WhitenoiseBattery,
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

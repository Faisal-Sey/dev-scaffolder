from typing import List

from batteries.base import BaseBattery
from batteries.express import (
    ExpressCORSBattery,
    ExpressHelmetBattery,
    ExpressMorganBattery,
    ExpressMongooseBattery,
    ExpressSequelizeBattery,
    ExpressPrismaBattery,
    ExpressJestBattery,
    ExpressGitHubActionsBattery,
    ExpressGitLabCIBattery,
    ExpressBitbucketPipelinesBattery,
    ExpressCircleCIBattery,
)
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
from batteries.fastify import (
    FastifyCORSBattery,
    FastifyHelmetBattery,
    FastifyMongooseBattery,
    FastifyPrismaBattery,
    FastifyJestBattery,
    FastifySequelizeBattery,
    FastifyMorganBattery,
    FastifySentryBattery,
    FastifyGitHubActionsBattery,
    FastifyGitLabCIBattery,
    FastifyBitbucketPipelinesBattery,
    FastifyCircleCIBattery,
)
from batteries.fastapi import (
    FastAPICORSBattery,
    FastAPISQLAlchemyBattery,
    FastAPITortoiseORMBattery,
    FastAPICeleryBattery,
    FastAPIPytestBattery,
    FastAPISentryBattery,
    FastAPIStructlogBattery,
    FastAPIGitHubActionsBattery,
    FastAPIGitLabCIBattery,
    FastAPIBitbucketPipelinesBattery,
    FastAPICircleCIBattery,
)
from batteries.nestjs import (
    NestJSCORSBattery,
    NestJSHelmetBattery,
    NestJSMongooseBattery,
    NestJSPrismaBattery,
    NestJSGitHubActionsBattery,
    NestJSGitLabCIBattery,
    NestJSBitbucketPipelinesBattery,
    NestJSCircleCIBattery,
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


EXPRESS_BATTERY_MAP = {
    # Middleware
    'cors': ExpressCORSBattery,
    'helmet': ExpressHelmetBattery,
    'morgan': ExpressMorganBattery,
    # Databases
    'mongoose': ExpressMongooseBattery,
    'sequelize': ExpressSequelizeBattery,
    'prisma': ExpressPrismaBattery,
    # Testing
    'jest': ExpressJestBattery,
    # CI/CD
    'github actions': ExpressGitHubActionsBattery,
    'gitlab ci': ExpressGitLabCIBattery,
    'bitbucket pipelines': ExpressBitbucketPipelinesBattery,
    'circleci': ExpressCircleCIBattery,
}


def parse_express_batteries(batteries_str: str) -> List[BaseBattery]:
    """
    Parse a comma-separated battery string into instantiated Express battery objects.

    :param batteries_str: Comma-separated battery names, e.g. "CORS,Helmet,Jest"
    :return: List of instantiated battery objects.
    """
    return [
        EXPRESS_BATTERY_MAP[name.strip().lower()]()
        for name in batteries_str.split(',')
        if name.strip().lower() in EXPRESS_BATTERY_MAP
    ]


FASTIFY_BATTERY_MAP = {
    # Middleware / Plugins
    'cors': FastifyCORSBattery,
    'helmet': FastifyHelmetBattery,
    'morgan': FastifyMorganBattery,
    # Databases
    'mongoose': FastifyMongooseBattery,
    'sequelize': FastifySequelizeBattery,
    'prisma': FastifyPrismaBattery,
    # Error tracking
    'sentry': FastifySentryBattery,
    # Testing
    'jest': FastifyJestBattery,
    # CI/CD
    'github actions': FastifyGitHubActionsBattery,
    'gitlab ci': FastifyGitLabCIBattery,
    'bitbucket pipelines': FastifyBitbucketPipelinesBattery,
    'circleci': FastifyCircleCIBattery,
}


def parse_fastify_batteries(batteries_str: str) -> List[BaseBattery]:
    """
    Parse a comma-separated battery string into instantiated Fastify battery objects.

    :param batteries_str: Comma-separated battery names, e.g. "CORS,Helmet,Jest"
    :return: List of instantiated battery objects.
    """
    return [
        FASTIFY_BATTERY_MAP[name.strip().lower()]()
        for name in batteries_str.split(',')
        if name.strip().lower() in FASTIFY_BATTERY_MAP
    ]


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
    # CI/CD
    'github actions': FastAPIGitHubActionsBattery,
    'gitlab ci': FastAPIGitLabCIBattery,
    'bitbucket pipelines': FastAPIBitbucketPipelinesBattery,
    'circleci': FastAPICircleCIBattery,
}


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


NESTJS_BATTERY_MAP = {
    # Middleware
    'cors': NestJSCORSBattery,
    'helmet': NestJSHelmetBattery,
    # Databases
    'mongoose': NestJSMongooseBattery,
    'prisma': NestJSPrismaBattery,
    # CI/CD
    'github actions': NestJSGitHubActionsBattery,
    'gitlab ci': NestJSGitLabCIBattery,
    'bitbucket pipelines': NestJSBitbucketPipelinesBattery,
    'circleci': NestJSCircleCIBattery,
}


def parse_nestjs_batteries(batteries_str: str) -> List[BaseBattery]:
    """
    Parse a comma-separated battery string into instantiated NestJS battery objects.

    :param batteries_str: Comma-separated battery names, e.g. "CORS,Helmet,Mongoose"
    :return: List of instantiated battery objects.
    """
    return [
        NESTJS_BATTERY_MAP[name.strip().lower()]()
        for name in batteries_str.split(',')
        if name.strip().lower() in NESTJS_BATTERY_MAP
    ]

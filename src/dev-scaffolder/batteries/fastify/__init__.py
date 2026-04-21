from .cors import FastifyCORSBattery
from .helmet import FastifyHelmetBattery
from .mongoose import FastifyMongooseBattery
from .prisma import FastifyPrismaBattery
from .jest import FastifyJestBattery
from .sequelize import FastifySequelizeBattery
from .morgan import FastifyMorganBattery
from .sentry import FastifySentryBattery
from .github_actions import FastifyGitHubActionsBattery
from .gitlab_ci import FastifyGitLabCIBattery
from .bitbucket_pipelines import FastifyBitbucketPipelinesBattery
from .circleci import FastifyCircleCIBattery

__all__ = [
    'FastifyCORSBattery',
    'FastifyHelmetBattery',
    'FastifyMongooseBattery',
    'FastifyPrismaBattery',
    'FastifyJestBattery',
    'FastifySequelizeBattery',
    'FastifyMorganBattery',
    'FastifySentryBattery',
    'FastifyGitHubActionsBattery',
    'FastifyGitLabCIBattery',
    'FastifyBitbucketPipelinesBattery',
    'FastifyCircleCIBattery',
]

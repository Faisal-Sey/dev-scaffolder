# ── Official ───────────────────────────────────────────────────────────────────

FASTIFY_PACKAGE_JSON = """\
{
  "name": "{project_name}",
  "version": "1.0.0",
  "description": "",
  "main": "src/index.js",
  "scripts": {
    "start": "node src/index.js",
    "dev": "nodemon src/index.js"
  },
  "dependencies": {
    "fastify": "^4.26.0",
    "dotenv": "^16.3.1"
  },
  "devDependencies": {
    "nodemon": "^3.0.2"
  }
}
"""

FASTIFY_INDEX_JS = """\
'use strict';

require('dotenv').config();
const app = require('./app');

const PORT = process.env.PORT || 3000;

const start = async () => {
  try {
    await app.listen({ port: PORT, host: '0.0.0.0' });
  } catch (err) {
    app.log.error(err);
    process.exit(1);
  }
};

start();
"""

FASTIFY_APP_JS = """\
'use strict';

const fastify = require('fastify')({ logger: true });

// [BATTERY:IMPORTS]

// [BATTERY:PLUGINS]

fastify.register(require('./routes/index'));

module.exports = fastify;
"""

FASTIFY_ROUTES_INDEX_JS = """\
'use strict';

async function routes(fastify) {
  fastify.get('/', async (request, reply) => {
    return { message: 'Welcome to {project_name}' };
  });

  fastify.get('/health', async (request, reply) => {
    return { status: 'ok' };
  });
}

module.exports = routes;
"""

FASTIFY_GITIGNORE = """\
node_modules/
.env
dist/
*.log
"""

FASTIFY_ENV = """\
PORT=3000
NODE_ENV=development
"""

FASTIFY_ENV_EXAMPLE = """\
PORT=3000
NODE_ENV=development
"""

# ── Docker ─────────────────────────────────────────────────────────────────────

FASTIFY_DOCKERFILE = """\
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .

EXPOSE 3000

CMD ["node", "src/index.js"]
"""

FASTIFY_DOCKER_COMPOSE = """\
services:
  web:
    build: .
    ports:
      - "3000:3000"
    volumes:
      - .:/app
      - /app/node_modules
    environment:
      - NODE_ENV=development
      - PORT=3000
    command: npm run dev
"""

FASTIFY_DOCKERIGNORE = """\
node_modules
.env
*.log
dist
.git
"""

# ── JWT Auth ───────────────────────────────────────────────────────────────────

FASTIFY_JWT_PACKAGE_JSON = """\
{
  "name": "{project_name}",
  "version": "1.0.0",
  "description": "",
  "main": "src/index.js",
  "scripts": {
    "start": "node src/index.js",
    "dev": "nodemon src/index.js"
  },
  "dependencies": {
    "fastify": "^4.26.0",
    "@fastify/jwt": "^8.0.0",
    "bcryptjs": "^2.4.3",
    "dotenv": "^16.3.1"
  },
  "devDependencies": {
    "nodemon": "^3.0.2"
  }
}
"""

FASTIFY_JWT_APP_JS = """\
'use strict';

const fastify = require('fastify')({ logger: true });

fastify.register(require('@fastify/jwt'), {
  secret: process.env.JWT_SECRET || 'changeme',
});

fastify.decorate('authenticate', async function (request, reply) {
  try {
    await request.jwtVerify();
  } catch (err) {
    reply.send(err);
  }
});

fastify.register(require('./routes/index'));
fastify.register(require('./routes/auth'));

module.exports = fastify;
"""

FASTIFY_JWT_AUTH_ROUTES_JS = """\
'use strict';

const bcrypt = require('bcryptjs');

// In-memory user store — replace with a database in production.
const users = [];

async function authRoutes(fastify) {
  fastify.post('/auth/register', async (request, reply) => {
    const { username, password } = request.body;
    if (users.find(u => u.username === username)) {
      return reply.code(409).send({ error: 'Username already taken' });
    }
    const hashed = await bcrypt.hash(password, 10);
    users.push({ id: users.length + 1, username, password: hashed });
    return reply.code(201).send({ message: 'User registered' });
  });

  fastify.post('/auth/login', async (request, reply) => {
    const { username, password } = request.body;
    const user = users.find(u => u.username === username);
    if (!user || !(await bcrypt.compare(password, user.password))) {
      return reply.code(401).send({ error: 'Invalid credentials' });
    }
    const token = fastify.jwt.sign(
      { id: user.id, username: user.username },
      { expiresIn: '15m' },
    );
    return { token };
  });

  fastify.get('/auth/me', {
    onRequest: [fastify.authenticate],
    handler: async (request) => request.user,
  });
}

module.exports = authRoutes;
"""

FASTIFY_JWT_ENV_EXAMPLE = """\
PORT=3000
NODE_ENV=development
JWT_SECRET=change_this_to_a_strong_secret
"""

# ── REST API ──────────────────────────────────────────────────────────────────

FASTIFY_REST_APP_JS = """\
'use strict';

const fastify = require('fastify')({ logger: true });

// [BATTERY:IMPORTS]

// [BATTERY:PLUGINS]

fastify.register(require('./routes/index'));
fastify.register(require('./routes/items'));

module.exports = fastify;
"""

FASTIFY_REST_ITEMS_ROUTES_JS = """\
'use strict';

let items = [];
let nextId = 1;

async function itemRoutes(fastify) {
  fastify.get('/items', async () => items);

  fastify.get('/items/:id', async (request, reply) => {
    const item = items.find(i => i.id === Number(request.params.id));
    if (!item) return reply.code(404).send({ error: 'Not found' });
    return item;
  });

  fastify.post('/items', async (request, reply) => {
    const item = { id: nextId++, ...request.body };
    items.push(item);
    return reply.code(201).send(item);
  });

  fastify.put('/items/:id', async (request, reply) => {
    const idx = items.findIndex(i => i.id === Number(request.params.id));
    if (idx === -1) return reply.code(404).send({ error: 'Not found' });
    items[idx] = { ...items[idx], ...request.body };
    return items[idx];
  });

  fastify.delete('/items/:id', async (request, reply) => {
    const idx = items.findIndex(i => i.id === Number(request.params.id));
    if (idx === -1) return reply.code(404).send({ error: 'Not found' });
    items.splice(idx, 1);
    return reply.code(204).send();
  });
}

module.exports = itemRoutes;
"""

# ── Prisma ────────────────────────────────────────────────────────────────────

FASTIFY_PRISMA_SCHEMA = """\
// Learn more: https://pris.ly/d/prisma-schema

generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = env("DB_PROVIDER")
  url      = env("DATABASE_URL")
}
"""

FASTIFY_PRISMA_DB_JS = """\
const { PrismaClient } = require('@prisma/client');

const prisma = new PrismaClient();

module.exports = { prisma };
"""

FASTIFY_PRISMA_IMPORT = "const { prisma } = require('./db');\n"

# ── Testing ───────────────────────────────────────────────────────────────────

FASTIFY_EXAMPLE_TEST_JS = """\
const build = require('../src/app');

describe('API', () => {
  let app;

  beforeAll(async () => {
    app = build;
    await app.ready();
  });

  afterAll(async () => {
    await app.close();
  });

  test('GET / returns welcome message', async () => {
    const res = await app.inject({ method: 'GET', url: '/' });
    expect(res.statusCode).toBe(200);
    expect(JSON.parse(res.body)).toHaveProperty('message');
  });

  test('GET /health returns ok', async () => {
    const res = await app.inject({ method: 'GET', url: '/health' });
    expect(res.statusCode).toBe(200);
    expect(JSON.parse(res.body)).toEqual({ status: 'ok' });
  });
});
"""

# ── Battery snippets ──────────────────────────────────────────────────────────

FASTIFY_CORS_IMPORT = "const cors = require('@fastify/cors');\n"
FASTIFY_CORS_PLUGIN = "fastify.register(cors);\n"

FASTIFY_HELMET_IMPORT = "const helmet = require('@fastify/helmet');\n"
FASTIFY_HELMET_PLUGIN = "fastify.register(helmet);\n"

FASTIFY_MONGOOSE_IMPORT = "const mongoose = require('mongoose');\n"
FASTIFY_MONGOOSE_SETUP = """\
mongoose.connect(process.env.MONGODB_URI || 'mongodb://localhost:27017/{project_name}')
  .then(() => fastify.log.info('MongoDB connected'))
  .catch((err) => { fastify.log.error(err); process.exit(1); });
"""

# ── CI/CD ─────────────────────────────────────────────────────────────────────

FASTIFY_GITHUB_ACTIONS_WORKFLOW = """\
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run tests
        run: npm test
"""

FASTIFY_GITLAB_CI = """\
image: node:20-alpine

stages:
  - test

test:
  stage: test
  cache:
    paths:
      - node_modules/
  script:
    - npm ci
    - npm test
  only:
    - main
    - merge_requests
"""

FASTIFY_BITBUCKET_PIPELINES = """\
image: node:20-alpine

pipelines:
  default:
    - step:
        name: Test
        caches:
          - node
        script:
          - npm ci
          - npm test
  branches:
    main:
      - step:
          name: Test
          caches:
            - node
          script:
            - npm ci
            - npm test
"""

FASTIFY_CIRCLECI_CONFIG = """\
version: 2.1

orbs:
  node: circleci/node@5

jobs:
  test:
    executor: node/default
    steps:
      - checkout
      - node/install-packages
      - run:
          name: Run tests
          command: npm test

workflows:
  test:
    jobs:
      - test
"""

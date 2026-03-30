# ── Official ───────────────────────────────────────────────────────────────────

EXPRESS_PACKAGE_JSON = """\
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
    "express": "^4.18.2",
    "dotenv": "^16.3.1"
  },
  "devDependencies": {
    "nodemon": "^3.0.2"
  }
}
"""

EXPRESS_INDEX_JS = """\
require('dotenv').config();
const app = require('./app');

const PORT = process.env.PORT || 3000;

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
"""

EXPRESS_APP_JS = """\
const express = require('express');
const indexRouter = require('./routes/index');

// [BATTERY:IMPORTS]

const app = express();

app.use(express.json());
app.use(express.urlencoded({ extended: false }));

// [BATTERY:MIDDLEWARE]

app.use('/', indexRouter);

module.exports = app;
"""

EXPRESS_ROUTES_INDEX_JS = """\
const express = require('express');
const router = express.Router();

router.get('/', (req, res) => {
  res.json({ message: 'Welcome to {project_name}' });
});

router.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

module.exports = router;
"""

EXPRESS_GITIGNORE = """\
node_modules/
.env
dist/
*.log
"""

EXPRESS_ENV = """\
PORT=3000
NODE_ENV=development
"""

EXPRESS_ENV_EXAMPLE = """\
PORT=3000
NODE_ENV=development
"""

# ── Docker ─────────────────────────────────────────────────────────────────────

EXPRESS_DOCKERFILE = """\
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .

EXPOSE 3000

CMD ["node", "src/index.js"]
"""

EXPRESS_DOCKER_COMPOSE = """\
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

EXPRESS_DOCKERIGNORE = """\
node_modules
.env
*.log
dist
.git
"""

# ── JWT Auth ───────────────────────────────────────────────────────────────────

EXPRESS_JWT_PACKAGE_JSON = """\
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
    "express": "^4.18.2",
    "dotenv": "^16.3.1",
    "jsonwebtoken": "^9.0.2",
    "bcryptjs": "^2.4.3"
  },
  "devDependencies": {
    "nodemon": "^3.0.2"
  }
}
"""

EXPRESS_JWT_APP_JS = """\
const express = require('express');
const indexRouter = require('./routes/index');
const authRouter = require('./routes/auth');

// [BATTERY:IMPORTS]

const app = express();

app.use(express.json());
app.use(express.urlencoded({ extended: false }));

// [BATTERY:MIDDLEWARE]

app.use('/', indexRouter);
app.use('/auth', authRouter);

module.exports = app;
"""

EXPRESS_JWT_AUTH_MIDDLEWARE_JS = """\
const jwt = require('jsonwebtoken');

function authenticateToken(req, res, next) {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];

  if (!token) {
    return res.status(401).json({ error: 'Access token required' });
  }

  try {
    const payload = jwt.verify(token, process.env.JWT_SECRET);
    req.user = payload;
    next();
  } catch (err) {
    return res.status(403).json({ error: 'Invalid or expired token' });
  }
}

module.exports = { authenticateToken };
"""

EXPRESS_JWT_AUTH_ROUTES_JS = """\
const express = require('express');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const { authenticateToken } = require('../middleware/auth');

const router = express.Router();

// In-memory user store (replace with a real database in production)
const users = [];

router.post('/register', async (req, res) => {
  const { username, password } = req.body;

  if (!username || !password) {
    return res.status(400).json({ error: 'Username and password are required' });
  }

  if (users.find(u => u.username === username)) {
    return res.status(409).json({ error: 'Username already exists' });
  }

  const hashedPassword = await bcrypt.hash(password, 10);
  const user = { id: Date.now(), username, password: hashedPassword };
  users.push(user);

  res.status(201).json({ message: 'User registered successfully' });
});

router.post('/login', async (req, res) => {
  const { username, password } = req.body;
  const user = users.find(u => u.username === username);

  if (!user || !(await bcrypt.compare(password, user.password))) {
    return res.status(401).json({ error: 'Invalid credentials' });
  }

  const accessToken = jwt.sign(
    { id: user.id, username: user.username },
    process.env.JWT_SECRET,
    { expiresIn: process.env.JWT_EXPIRES_IN || '15m' }
  );

  const refreshToken = jwt.sign(
    { id: user.id },
    process.env.JWT_REFRESH_SECRET,
    { expiresIn: '7d' }
  );

  res.json({ accessToken, refreshToken });
});

router.post('/refresh', (req, res) => {
  const { refreshToken } = req.body;

  if (!refreshToken) {
    return res.status(401).json({ error: 'Refresh token required' });
  }

  try {
    const payload = jwt.verify(refreshToken, process.env.JWT_REFRESH_SECRET);
    const accessToken = jwt.sign(
      { id: payload.id },
      process.env.JWT_SECRET,
      { expiresIn: process.env.JWT_EXPIRES_IN || '15m' }
    );
    res.json({ accessToken });
  } catch (err) {
    return res.status(403).json({ error: 'Invalid or expired refresh token' });
  }
});

router.get('/me', authenticateToken, (req, res) => {
  res.json({ user: req.user });
});

module.exports = router;
"""

EXPRESS_JWT_ENV_EXAMPLE = """\
PORT=3000
NODE_ENV=development
JWT_SECRET=your-super-secret-jwt-key-change-in-production
JWT_REFRESH_SECRET=your-super-secret-refresh-key-change-in-production
JWT_EXPIRES_IN=15m
"""

# ── WebSockets ─────────────────────────────────────────────────────────────────

EXPRESS_WS_PACKAGE_JSON = """\
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
    "express": "^4.18.2",
    "dotenv": "^16.3.1",
    "ws": "^8.16.0"
  },
  "devDependencies": {
    "nodemon": "^3.0.2"
  }
}
"""

EXPRESS_WS_INDEX_JS = """\
require('dotenv').config();
const http = require('http');
const app = require('./app');
const { setupWebSocket } = require('./websocket');

const PORT = process.env.PORT || 3000;

const server = http.createServer(app);
setupWebSocket(server);

server.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
  console.log(`WebSocket server ready at ws://localhost:${PORT}/ws`);
});
"""

EXPRESS_WS_WEBSOCKET_JS = """\
const { WebSocketServer } = require('ws');

function setupWebSocket(server) {
  const wss = new WebSocketServer({ server, path: '/ws' });
  const clients = new Map();

  wss.on('connection', (ws) => {
    const clientId = Date.now().toString();
    clients.set(clientId, ws);
    console.log(`Client ${clientId} connected`);

    ws.send(JSON.stringify({ type: 'connected', clientId }));

    ws.on('message', (data) => {
      let message;
      try {
        message = JSON.parse(data.toString());
      } catch {
        message = { type: 'text', content: data.toString() };
      }

      console.log(`Message from ${clientId}:`, message);

      clients.forEach((client, id) => {
        if (id !== clientId && client.readyState === 1) {
          client.send(JSON.stringify({ ...message, from: clientId }));
        }
      });
    });

    ws.on('close', () => {
      clients.delete(clientId);
      console.log(`Client ${clientId} disconnected`);
    });
  });

  return wss;
}

module.exports = { setupWebSocket };
"""

# ── Battery snippets ────────────────────────────────────────────────────────────

EXPRESS_CORS_IMPORT = "const cors = require('cors');\n"
EXPRESS_CORS_MIDDLEWARE = "app.use(cors());\n"

EXPRESS_HELMET_IMPORT = "const helmet = require('helmet');\n"
EXPRESS_HELMET_MIDDLEWARE = "app.use(helmet());\n"

EXPRESS_MORGAN_IMPORT = "const morgan = require('morgan');\n"
EXPRESS_MORGAN_MIDDLEWARE = "app.use(morgan('dev'));\n"

EXPRESS_MONGOOSE_IMPORT = "const mongoose = require('mongoose');\n"
EXPRESS_MONGOOSE_SETUP = """\
mongoose.connect(process.env.MONGODB_URI || 'mongodb://localhost:27017/{project_name}')
  .then(() => console.log('MongoDB connected'))
  .catch((err) => console.error('MongoDB connection error:', err));
"""

# ── Sequelize ─────────────────────────────────────────────────────────────────

EXPRESS_SEQUELIZE_DB_JS = """\
const { Sequelize } = require('sequelize');

const sequelize = new Sequelize(
  process.env.DATABASE_URL || 'sqlite::memory:',
  {
    dialect: process.env.DB_DIALECT || 'sqlite',
    logging: false,
  }
);

module.exports = { sequelize, Sequelize };
"""

EXPRESS_SEQUELIZE_IMPORT = "const { sequelize } = require('./db');\n"
EXPRESS_SEQUELIZE_SETUP = """\
sequelize.authenticate()
  .then(() => console.log('Database connected'))
  .catch((err) => console.error('Database connection error:', err));
"""

# ── CI/CD ─────────────────────────────────────────────────────────────────────

EXPRESS_GITHUB_ACTIONS_WORKFLOW = """\
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

EXPRESS_GITLAB_CI = """\
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

EXPRESS_BITBUCKET_PIPELINES = """\
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

EXPRESS_CIRCLECI_CONFIG = """\
version: 2.1

orbs:
  node: circleci/node@5

jobs:
  test:
    executor: node/default
    steps:
      - checkout
      - node/install-packages:
          pkg-manager: npm
      - run:
          name: Run tests
          command: npm test

workflows:
  test:
    jobs:
      - test
"""

# ── Prisma ────────────────────────────────────────────────────────────────────

EXPRESS_PRISMA_SCHEMA = """\
// Learn more: https://pris.ly/d/prisma-schema

generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = env("DB_PROVIDER")
  url      = env("DATABASE_URL")
}
"""

EXPRESS_PRISMA_DB_JS = """\
const { PrismaClient } = require('@prisma/client');

const prisma = new PrismaClient();

module.exports = { prisma };
"""

EXPRESS_PRISMA_IMPORT = "const { prisma } = require('./db');\n"

# ── Socket.IO ──────────────────────────────────────────────────────────────────

EXPRESS_SOCKETIO_PACKAGE_JSON = """\
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
    "express": "^4.18.2",
    "dotenv": "^16.3.1",
    "socket.io": "^4.7.4"
  },
  "devDependencies": {
    "nodemon": "^3.0.2"
  }
}
"""

EXPRESS_SOCKETIO_INDEX_JS = """\
require('dotenv').config();
const http = require('http');
const app = require('./app');
const { setupSocket } = require('./socket');

const PORT = process.env.PORT || 3000;

const server = http.createServer(app);
setupSocket(server);

server.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
  console.log(`Socket.IO ready at http://localhost:${PORT}`);
});
"""

EXPRESS_SOCKETIO_SOCKET_JS = """\
const { Server } = require('socket.io');

function setupSocket(server) {
  const io = new Server(server, {
    cors: {
      origin: '*',
      methods: ['GET', 'POST'],
    },
  });

  io.on('connection', (socket) => {
    console.log(`Client connected: ${socket.id}`);

    // Broadcast a message to all other connected clients
    socket.on('message', (data) => {
      console.log(`Message from ${socket.id}:`, data);
      socket.broadcast.emit('message', { ...data, from: socket.id });
    });

    // Join a named room
    socket.on('join_room', (room) => {
      socket.join(room);
      console.log(`${socket.id} joined room: ${room}`);
      socket.to(room).emit('user_joined', { userId: socket.id, room });
    });

    // Send a message to everyone in a room
    socket.on('room_message', ({ room, message }) => {
      socket.to(room).emit('room_message', { from: socket.id, message });
    });

    socket.on('disconnect', () => {
      console.log(`Client disconnected: ${socket.id}`);
    });
  });

  return io;
}

module.exports = { setupSocket };
"""

EXPRESS_JEST_CONFIG = """\
  "jest": {
    "testEnvironment": "node"
  }
"""

EXPRESS_EXAMPLE_TEST_JS = """\
const request = require('supertest');
const app = require('../src/app');

describe('GET /', () => {
  it('should return welcome message', async () => {
    const res = await request(app).get('/');
    expect(res.statusCode).toBe(200);
    expect(res.body).toHaveProperty('message');
  });
});

describe('GET /health', () => {
  it('should return ok status', async () => {
    const res = await request(app).get('/health');
    expect(res.statusCode).toBe(200);
    expect(res.body.status).toBe('ok');
  });
});
"""

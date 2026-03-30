# ── Official ───────────────────────────────────────────────────────────────────

EXPRESS_TS_TSCONFIG = """\
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "lib": ["ES2020"],
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
"""

EXPRESS_TS_PACKAGE_JSON = """\
{
  "name": "{project_name}",
  "version": "1.0.0",
  "description": "",
  "main": "dist/index.js",
  "scripts": {
    "build": "tsc",
    "start": "node dist/index.js",
    "dev": "tsx watch src/index.ts"
  },
  "dependencies": {
    "express": "^4.18.2",
    "dotenv": "^16.3.1"
  },
  "devDependencies": {
    "@types/express": "^4.17.21",
    "@types/node": "^20.11.5",
    "typescript": "^5.3.3",
    "tsx": "^4.7.0"
  }
}
"""

EXPRESS_TS_INDEX_TS = """\
import 'dotenv/config';
import app from './app';

const PORT = process.env.PORT || 3000;

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
"""

EXPRESS_TS_APP_TS = """\
import express, { Application } from 'express';
import indexRouter from './routes/index';

// [BATTERY:IMPORTS]

const app: Application = express();

app.use(express.json());
app.use(express.urlencoded({ extended: false }));

// [BATTERY:MIDDLEWARE]

app.use('/', indexRouter);

export default app;
"""

EXPRESS_TS_ROUTES_INDEX_TS = """\
import { Router, Request, Response } from 'express';

const router = Router();

router.get('/', (_req: Request, res: Response) => {
  res.json({ message: 'Welcome to {project_name}' });
});

router.get('/health', (_req: Request, res: Response) => {
  res.json({ status: 'ok' });
});

export default router;
"""

EXPRESS_TS_GITIGNORE = """\
node_modules/
.env
dist/
*.log
"""

EXPRESS_TS_ENV = """\
PORT=3000
NODE_ENV=development
"""

EXPRESS_TS_ENV_EXAMPLE = """\
PORT=3000
NODE_ENV=development
"""

# ── Docker ─────────────────────────────────────────────────────────────────────

EXPRESS_TS_DOCKERFILE = """\
# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json tsconfig.json ./
RUN npm ci

COPY src ./src
RUN npm run build

# Production stage
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY --from=builder /app/dist ./dist

EXPOSE 3000

CMD ["node", "dist/index.js"]
"""

EXPRESS_TS_DOCKER_COMPOSE = """\
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

EXPRESS_TS_DOCKERIGNORE = """\
node_modules
.env
dist/
*.log
.git
"""

# ── JWT Auth ───────────────────────────────────────────────────────────────────

EXPRESS_TS_JWT_PACKAGE_JSON = """\
{
  "name": "{project_name}",
  "version": "1.0.0",
  "description": "",
  "main": "dist/index.js",
  "scripts": {
    "build": "tsc",
    "start": "node dist/index.js",
    "dev": "tsx watch src/index.ts"
  },
  "dependencies": {
    "express": "^4.18.2",
    "dotenv": "^16.3.1",
    "jsonwebtoken": "^9.0.2",
    "bcryptjs": "^2.4.3"
  },
  "devDependencies": {
    "@types/express": "^4.17.21",
    "@types/node": "^20.11.5",
    "@types/jsonwebtoken": "^9.0.5",
    "@types/bcryptjs": "^2.4.6",
    "typescript": "^5.3.3",
    "tsx": "^4.7.0"
  }
}
"""

EXPRESS_TS_JWT_APP_TS = """\
import express, { Application } from 'express';
import indexRouter from './routes/index';
import authRouter from './routes/auth';

// [BATTERY:IMPORTS]

const app: Application = express();

app.use(express.json());
app.use(express.urlencoded({ extended: false }));

// [BATTERY:MIDDLEWARE]

app.use('/', indexRouter);
app.use('/auth', authRouter);

export default app;
"""

EXPRESS_TS_JWT_AUTH_MIDDLEWARE_TS = """\
import { Request, Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';

export interface AuthRequest extends Request {
  user?: jwt.JwtPayload;
}

export function authenticateToken(
  req: AuthRequest,
  res: Response,
  next: NextFunction
): void {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];

  if (!token) {
    res.status(401).json({ error: 'Access token required' });
    return;
  }

  try {
    const payload = jwt.verify(token, process.env.JWT_SECRET as string) as jwt.JwtPayload;
    req.user = payload;
    next();
  } catch {
    res.status(403).json({ error: 'Invalid or expired token' });
  }
}
"""

EXPRESS_TS_JWT_AUTH_ROUTES_TS = """\
import { Router, Request, Response } from 'express';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import { authenticateToken, AuthRequest } from '../middleware/auth';

const router = Router();

interface User {
  id: number;
  username: string;
  password: string;
}

// In-memory user store (replace with a real database in production)
const users: User[] = [];

router.post('/register', async (req: Request, res: Response): Promise<void> => {
  const { username, password } = req.body as { username: string; password: string };

  if (!username || !password) {
    res.status(400).json({ error: 'Username and password are required' });
    return;
  }

  if (users.find((u) => u.username === username)) {
    res.status(409).json({ error: 'Username already exists' });
    return;
  }

  const hashedPassword = await bcrypt.hash(password, 10);
  const user: User = { id: Date.now(), username, password: hashedPassword };
  users.push(user);

  res.status(201).json({ message: 'User registered successfully' });
});

router.post('/login', async (req: Request, res: Response): Promise<void> => {
  const { username, password } = req.body as { username: string; password: string };
  const user = users.find((u) => u.username === username);

  if (!user || !(await bcrypt.compare(password, user.password))) {
    res.status(401).json({ error: 'Invalid credentials' });
    return;
  }

  const accessToken = jwt.sign(
    { id: user.id, username: user.username },
    process.env.JWT_SECRET as string,
    { expiresIn: (process.env.JWT_EXPIRES_IN || '15m') as jwt.SignOptions['expiresIn'] }
  );

  const refreshToken = jwt.sign(
    { id: user.id },
    process.env.JWT_REFRESH_SECRET as string,
    { expiresIn: '7d' }
  );

  res.json({ accessToken, refreshToken });
});

router.post('/refresh', (req: Request, res: Response): void => {
  const { refreshToken } = req.body as { refreshToken: string };

  if (!refreshToken) {
    res.status(401).json({ error: 'Refresh token required' });
    return;
  }

  try {
    const payload = jwt.verify(
      refreshToken,
      process.env.JWT_REFRESH_SECRET as string
    ) as jwt.JwtPayload;

    const accessToken = jwt.sign(
      { id: payload.id },
      process.env.JWT_SECRET as string,
      { expiresIn: (process.env.JWT_EXPIRES_IN || '15m') as jwt.SignOptions['expiresIn'] }
    );
    res.json({ accessToken });
  } catch {
    res.status(403).json({ error: 'Invalid or expired refresh token' });
  }
});

router.get('/me', authenticateToken, (req: AuthRequest, res: Response): void => {
  res.json({ user: req.user });
});

export default router;
"""

EXPRESS_TS_JWT_ENV_EXAMPLE = """\
PORT=3000
NODE_ENV=development
JWT_SECRET=your-super-secret-jwt-key-change-in-production
JWT_REFRESH_SECRET=your-super-secret-refresh-key-change-in-production
JWT_EXPIRES_IN=15m
"""

# ── WebSockets ─────────────────────────────────────────────────────────────────

EXPRESS_TS_WS_PACKAGE_JSON = """\
{
  "name": "{project_name}",
  "version": "1.0.0",
  "description": "",
  "main": "dist/index.js",
  "scripts": {
    "build": "tsc",
    "start": "node dist/index.js",
    "dev": "tsx watch src/index.ts"
  },
  "dependencies": {
    "express": "^4.18.2",
    "dotenv": "^16.3.1",
    "ws": "^8.16.0"
  },
  "devDependencies": {
    "@types/express": "^4.17.21",
    "@types/node": "^20.11.5",
    "@types/ws": "^8.5.10",
    "typescript": "^5.3.3",
    "tsx": "^4.7.0"
  }
}
"""

EXPRESS_TS_WS_INDEX_TS = """\
import 'dotenv/config';
import http from 'http';
import app from './app';
import { setupWebSocket } from './websocket';

const PORT = process.env.PORT || 3000;

const server = http.createServer(app);
setupWebSocket(server);

server.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
  console.log(`WebSocket server ready at ws://localhost:${PORT}/ws`);
});
"""

EXPRESS_TS_WS_WEBSOCKET_TS = """\
import http from 'http';
import { WebSocketServer, WebSocket } from 'ws';

export function setupWebSocket(server: http.Server): WebSocketServer {
  const wss = new WebSocketServer({ server, path: '/ws' });
  const clients = new Map<string, WebSocket>();

  wss.on('connection', (ws: WebSocket) => {
    const clientId = Date.now().toString();
    clients.set(clientId, ws);
    console.log(`Client ${clientId} connected`);

    ws.send(JSON.stringify({ type: 'connected', clientId }));

    ws.on('message', (data: Buffer) => {
      let message: Record<string, unknown>;
      try {
        message = JSON.parse(data.toString()) as Record<string, unknown>;
      } catch {
        message = { type: 'text', content: data.toString() };
      }

      console.log(`Message from ${clientId}:`, message);

      clients.forEach((client, id) => {
        if (id !== clientId && client.readyState === WebSocket.OPEN) {
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
"""

# ── Socket.IO ──────────────────────────────────────────────────────────────────

EXPRESS_TS_SOCKETIO_PACKAGE_JSON = """\
{
  "name": "{project_name}",
  "version": "1.0.0",
  "description": "",
  "main": "dist/index.js",
  "scripts": {
    "build": "tsc",
    "start": "node dist/index.js",
    "dev": "tsx watch src/index.ts"
  },
  "dependencies": {
    "express": "^4.18.2",
    "dotenv": "^16.3.1",
    "socket.io": "^4.7.4"
  },
  "devDependencies": {
    "@types/express": "^4.17.21",
    "@types/node": "^20.11.5",
    "typescript": "^5.3.3",
    "tsx": "^4.7.0"
  }
}
"""

EXPRESS_TS_SOCKETIO_INDEX_TS = """\
import 'dotenv/config';
import http from 'http';
import app from './app';
import { setupSocket } from './socket';

const PORT = process.env.PORT || 3000;

const server = http.createServer(app);
setupSocket(server);

server.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
  console.log(`Socket.IO ready at http://localhost:${PORT}`);
});
"""

EXPRESS_TS_SOCKETIO_SOCKET_TS = """\
import http from 'http';
import { Server } from 'socket.io';

export function setupSocket(server: http.Server): Server {
  const io = new Server(server, {
    cors: {
      origin: '*',
      methods: ['GET', 'POST'],
    },
  });

  io.on('connection', (socket) => {
    console.log(`Client connected: ${socket.id}`);

    socket.on('message', (data: Record<string, unknown>) => {
      console.log(`Message from ${socket.id}:`, data);
      socket.broadcast.emit('message', { ...data, from: socket.id });
    });

    socket.on('join_room', (room: string) => {
      void socket.join(room);
      console.log(`${socket.id} joined room: ${room}`);
      socket.to(room).emit('user_joined', { userId: socket.id, room });
    });

    socket.on('room_message', ({ room, message }: { room: string; message: unknown }) => {
      socket.to(room).emit('room_message', { from: socket.id, message });
    });

    socket.on('disconnect', () => {
      console.log(`Client disconnected: ${socket.id}`);
    });
  });

  return io;
}
"""

# ── Battery snippets ────────────────────────────────────────────────────────────

EXPRESS_TS_CORS_IMPORT = "import cors from 'cors';\n"
EXPRESS_TS_CORS_MIDDLEWARE = "app.use(cors());\n"

EXPRESS_TS_HELMET_IMPORT = "import helmet from 'helmet';\n"
EXPRESS_TS_HELMET_MIDDLEWARE = "app.use(helmet());\n"

EXPRESS_TS_MORGAN_IMPORT = "import morgan from 'morgan';\n"
EXPRESS_TS_MORGAN_MIDDLEWARE = "app.use(morgan('dev'));\n"

EXPRESS_TS_MONGOOSE_IMPORT = "import mongoose from 'mongoose';\n"
EXPRESS_TS_MONGOOSE_SETUP = """\
mongoose
  .connect(process.env.MONGODB_URI || 'mongodb://localhost:27017/{project_name}')
  .then(() => console.log('MongoDB connected'))
  .catch((err: Error) => console.error('MongoDB connection error:', err));
"""

EXPRESS_TS_SEQUELIZE_DB_TS = """\
import { Sequelize } from 'sequelize';

const sequelize = new Sequelize(
  process.env.DATABASE_URL || 'sqlite::memory:',
  {
    dialect: (process.env.DB_DIALECT as 'sqlite' | 'postgres' | 'mysql') || 'sqlite',
    logging: false,
  }
);

export { sequelize, Sequelize };
"""

EXPRESS_TS_SEQUELIZE_IMPORT = "import { sequelize } from './db';\n"
EXPRESS_TS_SEQUELIZE_SETUP = """\
sequelize
  .authenticate()
  .then(() => console.log('Database connected'))
  .catch((err: Error) => console.error('Database connection error:', err));
"""

EXPRESS_TS_PRISMA_DB_TS = """\
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

export { prisma };
"""

EXPRESS_TS_PRISMA_IMPORT = "import { prisma } from './db';\n"

EXPRESS_TS_JEST_EXAMPLE_TEST_TS = """\
import request from 'supertest';
import app from '../src/app';

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

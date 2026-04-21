# ── Official ────────────────────────────────────────────────────────────────

NESTJS_PACKAGE_JSON = """\
{
  "name": "{project_name}",
  "version": "1.0.0",
  "description": "",
  "scripts": {
    "build": "nest build",
    "start": "nest start",
    "start:dev": "nest start --watch",
    "start:prod": "node dist/main",
    "test": "jest",
    "test:cov": "jest --coverage",
    "test:e2e": "jest --config ./test/jest-e2e.json"
  },
  "dependencies": {
    "@nestjs/common": "^10.0.0",
    "@nestjs/core": "^10.0.0",
    "@nestjs/platform-express": "^10.0.0",
    "dotenv": "^16.4.5",
    "reflect-metadata": "^0.2.2",
    "rxjs": "^7.8.1"
  },
  "devDependencies": {
    "@nestjs/cli": "^10.0.0",
    "@nestjs/schematics": "^10.0.0",
    "@nestjs/testing": "^10.0.0",
    "@types/express": "^4.17.21",
    "@types/jest": "^29.5.12",
    "@types/node": "^20.14.2",
    "@types/supertest": "^6.0.2",
    "jest": "^29.7.0",
    "source-map-support": "^0.5.21",
    "supertest": "^7.0.0",
    "ts-jest": "^29.1.5",
    "ts-node": "^10.9.2",
    "tslib": "^2.6.3",
    "typescript": "^5.4.5"
  },
  "jest": {
    "moduleFileExtensions": ["js", "json", "ts"],
    "rootDir": "src",
    "testRegex": ".*\\\\.spec\\\\.ts$",
    "transform": {
      "^.+\\\\.(t|j)s$": "ts-jest"
    },
    "collectCoverageFrom": ["**/*.(t|j)s"],
    "coverageDirectory": "../coverage",
    "testEnvironment": "node"
  }
}
"""

NESTJS_TSCONFIG = """\
{
  "compilerOptions": {
    "module": "commonjs",
    "declaration": true,
    "removeComments": true,
    "emitDecoratorMetadata": true,
    "experimentalDecorators": true,
    "allowSyntheticDefaultImports": true,
    "target": "ES2021",
    "sourceMap": true,
    "outDir": "./dist",
    "baseUrl": "./",
    "incremental": true,
    "skipLibCheck": true,
    "strictNullChecks": false,
    "noImplicitAny": false,
    "strictBindCallApply": false,
    "forceConsistentCasingInFileNames": false,
    "noFallthroughCasesInSwitch": false
  }
}
"""

NESTJS_TSCONFIG_BUILD = """\
{
  "extends": "./tsconfig.json",
  "exclude": ["node_modules", "test", "dist", "**/*spec.ts"]
}
"""

NESTJS_MAIN_TS = """\
import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import * as dotenv from 'dotenv';

dotenv.config();

// [BATTERY:IMPORTS]

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  // [BATTERY:SETUP]
  const port = process.env.PORT || 3000;
  await app.listen(port);
  console.log(`Application is running on: http://localhost:${port}`);
}
bootstrap();
"""

NESTJS_APP_MODULE_TS = """\
import { Module } from '@nestjs/common';
import { AppController } from './app.controller';
import { AppService } from './app.service';
// [BATTERY:IMPORTS]

@Module({
  imports: [
    // [BATTERY:MODULE_IMPORTS]
  ],
  controllers: [AppController],
  providers: [AppService],
})
export class AppModule {}
"""

NESTJS_APP_CONTROLLER_TS = """\
import { Controller, Get } from '@nestjs/common';
import { AppService } from './app.service';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Get()
  getRoot(): { message: string } {
    return { message: this.appService.getHello() };
  }

  @Get('health')
  getHealth(): { status: string } {
    return { status: 'ok' };
  }
}
"""

NESTJS_APP_SERVICE_TS = """\
import { Injectable } from '@nestjs/common';

@Injectable()
export class AppService {
  getHello(): string {
    return 'Welcome to {project_name}!';
  }
}
"""

NESTJS_APP_CONTROLLER_SPEC_TS = """\
import { Test, TestingModule } from '@nestjs/testing';
import { AppController } from './app.controller';
import { AppService } from './app.service';

describe('AppController', () => {
  let appController: AppController;

  beforeEach(async () => {
    const app: TestingModule = await Test.createTestingModule({
      controllers: [AppController],
      providers: [AppService],
    }).compile();

    appController = app.get<AppController>(AppController);
  });

  it('should return welcome message', () => {
    const result = appController.getRoot();
    expect(result).toHaveProperty('message');
  });

  it('should return health ok', () => {
    expect(appController.getHealth()).toEqual({ status: 'ok' });
  });
});
"""

NESTJS_GITIGNORE = """\
node_modules/
dist/
.env
*.log
coverage/
"""

NESTJS_ENV = """\
PORT=3000
NODE_ENV=development
"""

NESTJS_ENV_EXAMPLE = """\
PORT=3000
NODE_ENV=development
"""

NESTJS_NEST_CLI_JSON = """\
{
  "$schema": "https://json.schemastore.org/nest-cli",
  "collection": "@nestjs/schematics",
  "sourceRoot": "src",
  "compilerOptions": {
    "deleteOutDir": true
  }
}
"""

# ── REST API ──────────────────────────────────────────────────────────────────

NESTJS_REST_APP_MODULE_TS = """\
import { Module } from '@nestjs/common';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { ItemsModule } from './items/items.module';

@Module({
  imports: [ItemsModule],
  controllers: [AppController],
  providers: [AppService],
})
export class AppModule {}
"""

NESTJS_ITEMS_MODULE_TS = """\
import { Module } from '@nestjs/common';
import { ItemsController } from './items.controller';
import { ItemsService } from './items.service';

@Module({
  controllers: [ItemsController],
  providers: [ItemsService],
})
export class ItemsModule {}
"""

NESTJS_ITEMS_CONTROLLER_TS = """\
import {
  Controller,
  Get,
  Post,
  Put,
  Delete,
  Body,
  Param,
  HttpCode,
  HttpStatus,
} from '@nestjs/common';
import { ItemsService } from './items.service';
import { CreateItemDto } from './dto/create-item.dto';
import { UpdateItemDto } from './dto/update-item.dto';

@Controller('items')
export class ItemsController {
  constructor(private readonly itemsService: ItemsService) {}

  @Get()
  findAll() {
    return this.itemsService.findAll();
  }

  @Get(':id')
  findOne(@Param('id') id: string) {
    return this.itemsService.findOne(+id);
  }

  @Post()
  @HttpCode(HttpStatus.CREATED)
  create(@Body() createItemDto: CreateItemDto) {
    return this.itemsService.create(createItemDto);
  }

  @Put(':id')
  update(@Param('id') id: string, @Body() updateItemDto: UpdateItemDto) {
    return this.itemsService.update(+id, updateItemDto);
  }

  @Delete(':id')
  @HttpCode(HttpStatus.NO_CONTENT)
  remove(@Param('id') id: string) {
    return this.itemsService.remove(+id);
  }
}
"""

NESTJS_ITEMS_SERVICE_TS = """\
import { Injectable, NotFoundException } from '@nestjs/common';
import { CreateItemDto } from './dto/create-item.dto';
import { UpdateItemDto } from './dto/update-item.dto';

export interface Item {
  id: number;
  name: string;
  description?: string;
}

@Injectable()
export class ItemsService {
  private items: Item[] = [];
  private nextId = 1;

  findAll(): Item[] {
    return this.items;
  }

  findOne(id: number): Item {
    const item = this.items.find((i) => i.id === id);
    if (!item) throw new NotFoundException(`Item #${id} not found`);
    return item;
  }

  create(dto: CreateItemDto): Item {
    const item: Item = { id: this.nextId++, ...dto };
    this.items.push(item);
    return item;
  }

  update(id: number, dto: UpdateItemDto): Item {
    const item = this.findOne(id);
    Object.assign(item, dto);
    return item;
  }

  remove(id: number): void {
    const idx = this.items.findIndex((i) => i.id === id);
    if (idx === -1) throw new NotFoundException(`Item #${id} not found`);
    this.items.splice(idx, 1);
  }
}
"""

NESTJS_CREATE_ITEM_DTO_TS = """\
export class CreateItemDto {
  name: string;
  description?: string;
}
"""

NESTJS_UPDATE_ITEM_DTO_TS = """\
export class UpdateItemDto {
  name?: string;
  description?: string;
}
"""

# ── JWT Auth ──────────────────────────────────────────────────────────────────

NESTJS_JWT_PACKAGE_JSON = """\
{
  "name": "{project_name}",
  "version": "1.0.0",
  "description": "",
  "scripts": {
    "build": "nest build",
    "start": "nest start",
    "start:dev": "nest start --watch",
    "start:prod": "node dist/main",
    "test": "jest",
    "test:cov": "jest --coverage",
    "test:e2e": "jest --config ./test/jest-e2e.json"
  },
  "dependencies": {
    "@nestjs/common": "^10.0.0",
    "@nestjs/core": "^10.0.0",
    "@nestjs/jwt": "^10.2.0",
    "@nestjs/passport": "^10.0.3",
    "@nestjs/platform-express": "^10.0.0",
    "bcryptjs": "^2.4.3",
    "dotenv": "^16.4.5",
    "passport": "^0.7.0",
    "passport-jwt": "^4.0.1",
    "reflect-metadata": "^0.2.2",
    "rxjs": "^7.8.1"
  },
  "devDependencies": {
    "@nestjs/cli": "^10.0.0",
    "@nestjs/schematics": "^10.0.0",
    "@nestjs/testing": "^10.0.0",
    "@types/bcryptjs": "^2.4.6",
    "@types/express": "^4.17.21",
    "@types/jest": "^29.5.12",
    "@types/node": "^20.14.2",
    "@types/passport-jwt": "^4.0.1",
    "@types/supertest": "^6.0.2",
    "jest": "^29.7.0",
    "source-map-support": "^0.5.21",
    "supertest": "^7.0.0",
    "ts-jest": "^29.1.5",
    "ts-node": "^10.9.2",
    "tslib": "^2.6.3",
    "typescript": "^5.4.5"
  },
  "jest": {
    "moduleFileExtensions": ["js", "json", "ts"],
    "rootDir": "src",
    "testRegex": ".*\\\\.spec\\\\.ts$",
    "transform": {
      "^.+\\\\.(t|j)s$": "ts-jest"
    },
    "collectCoverageFrom": ["**/*.(t|j)s"],
    "coverageDirectory": "../coverage",
    "testEnvironment": "node"
  }
}
"""

NESTJS_JWT_APP_MODULE_TS = """\
import { Module } from '@nestjs/common';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { AuthModule } from './auth/auth.module';
import { UsersModule } from './users/users.module';

@Module({
  imports: [AuthModule, UsersModule],
  controllers: [AppController],
  providers: [AppService],
})
export class AppModule {}
"""

NESTJS_AUTH_MODULE_TS = """\
import { Module } from '@nestjs/common';
import { JwtModule } from '@nestjs/jwt';
import { PassportModule } from '@nestjs/passport';
import { AuthController } from './auth.controller';
import { AuthService } from './auth.service';
import { JwtStrategy } from './jwt.strategy';
import { UsersModule } from '../users/users.module';

@Module({
  imports: [
    UsersModule,
    PassportModule,
    JwtModule.register({
      secret: process.env.JWT_SECRET || 'changeme',
      signOptions: { expiresIn: '15m' },
    }),
  ],
  controllers: [AuthController],
  providers: [AuthService, JwtStrategy],
  exports: [AuthService],
})
export class AuthModule {}
"""

NESTJS_AUTH_SERVICE_TS = """\
import { Injectable, UnauthorizedException } from '@nestjs/common';
import { JwtService } from '@nestjs/jwt';
import * as bcrypt from 'bcryptjs';
import { UsersService } from '../users/users.service';

@Injectable()
export class AuthService {
  constructor(
    private readonly usersService: UsersService,
    private readonly jwtService: JwtService,
  ) {}

  async register(username: string, password: string) {
    const hashed = await bcrypt.hash(password, 10);
    return this.usersService.create(username, hashed);
  }

  async login(username: string, password: string) {
    const user = await this.usersService.findByUsername(username);
    if (!user || !(await bcrypt.compare(password, user.password))) {
      throw new UnauthorizedException('Invalid credentials');
    }
    const payload = { sub: user.id, username: user.username };
    return { access_token: this.jwtService.sign(payload) };
  }
}
"""

NESTJS_AUTH_CONTROLLER_TS = """\
import { Controller, Post, Body, HttpCode, HttpStatus } from '@nestjs/common';
import { AuthService } from './auth.service';

@Controller('auth')
export class AuthController {
  constructor(private readonly authService: AuthService) {}

  @Post('register')
  @HttpCode(HttpStatus.CREATED)
  register(@Body() body: { username: string; password: string }) {
    return this.authService.register(body.username, body.password);
  }

  @Post('login')
  @HttpCode(HttpStatus.OK)
  login(@Body() body: { username: string; password: string }) {
    return this.authService.login(body.username, body.password);
  }
}
"""

NESTJS_JWT_STRATEGY_TS = """\
import { Injectable } from '@nestjs/common';
import { PassportStrategy } from '@nestjs/passport';
import { ExtractJwt, Strategy } from 'passport-jwt';

@Injectable()
export class JwtStrategy extends PassportStrategy(Strategy) {
  constructor() {
    super({
      jwtFromRequest: ExtractJwt.fromAuthHeaderAsBearerToken(),
      ignoreExpiration: false,
      secretOrKey: process.env.JWT_SECRET || 'changeme',
    });
  }

  async validate(payload: any) {
    return { id: payload.sub, username: payload.username };
  }
}
"""

NESTJS_JWT_AUTH_GUARD_TS = """\
import { Injectable } from '@nestjs/common';
import { AuthGuard } from '@nestjs/passport';

@Injectable()
export class JwtAuthGuard extends AuthGuard('jwt') {}
"""

NESTJS_USERS_MODULE_TS = """\
import { Module } from '@nestjs/common';
import { UsersService } from './users.service';

@Module({
  providers: [UsersService],
  exports: [UsersService],
})
export class UsersModule {}
"""

NESTJS_USERS_SERVICE_TS = """\
import { Injectable, ConflictException } from '@nestjs/common';

export interface User {
  id: number;
  username: string;
  password: string;
}

@Injectable()
export class UsersService {
  private users: User[] = [];
  private nextId = 1;

  async create(username: string, password: string): Promise<Omit<User, 'password'>> {
    if (this.users.find((u) => u.username === username)) {
      throw new ConflictException('Username already taken');
    }
    const user: User = { id: this.nextId++, username, password };
    this.users.push(user);
    const { password: _pw, ...rest } = user;
    return rest;
  }

  async findByUsername(username: string): Promise<User | undefined> {
    return this.users.find((u) => u.username === username);
  }
}
"""

NESTJS_JWT_ENV_EXAMPLE = """\
PORT=3000
NODE_ENV=development
JWT_SECRET=change_this_to_a_strong_secret
"""

# ── Docker ─────────────────────────────────────────────────────────────────────

NESTJS_DOCKERFILE = """\
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --omit=dev
COPY --from=builder /app/dist ./dist
EXPOSE 3000
CMD ["node", "dist/main"]
"""

NESTJS_DOCKER_COMPOSE = """\
services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=development
      - PORT=3000
    volumes:
      - .:/app
      - /app/node_modules
    command: npm run start:dev
"""

NESTJS_DOCKERIGNORE = """\
node_modules
dist
.env
*.log
.git
coverage
"""

# ── TypeORM ────────────────────────────────────────────────────────────────────

NESTJS_TYPEORM_PACKAGE_JSON = """\
{
  "name": "{project_name}",
  "version": "1.0.0",
  "description": "",
  "scripts": {
    "build": "nest build",
    "start": "nest start",
    "start:dev": "nest start --watch",
    "start:prod": "node dist/main",
    "test": "jest",
    "test:cov": "jest --coverage"
  },
  "dependencies": {
    "@nestjs/common": "^10.0.0",
    "@nestjs/core": "^10.0.0",
    "@nestjs/platform-express": "^10.0.0",
    "@nestjs/typeorm": "^10.0.2",
    "better-sqlite3": "^9.4.3",
    "dotenv": "^16.4.5",
    "reflect-metadata": "^0.2.2",
    "rxjs": "^7.8.1",
    "typeorm": "^0.3.20"
  },
  "devDependencies": {
    "@nestjs/cli": "^10.0.0",
    "@nestjs/schematics": "^10.0.0",
    "@nestjs/testing": "^10.0.0",
    "@types/better-sqlite3": "^7.6.9",
    "@types/jest": "^29.5.12",
    "@types/node": "^20.14.2",
    "jest": "^29.7.0",
    "ts-jest": "^29.1.5",
    "ts-node": "^10.9.2",
    "tslib": "^2.6.3",
    "typescript": "^5.4.5"
  },
  "jest": {
    "moduleFileExtensions": ["js", "json", "ts"],
    "rootDir": "src",
    "testRegex": ".*\\\\.spec\\\\.ts$",
    "transform": {
      "^.+\\\\.(t|j)s$": "ts-jest"
    },
    "collectCoverageFrom": ["**/*.(t|j)s"],
    "coverageDirectory": "../coverage",
    "testEnvironment": "node"
  }
}
"""

NESTJS_TYPEORM_APP_MODULE_TS = """\
import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { UsersModule } from './users/users.module';
import { User } from './users/user.entity';

@Module({
  imports: [
    TypeOrmModule.forRoot({
      type: 'better-sqlite3',
      database: 'data/database.sqlite',
      entities: [User],
      synchronize: true,
    }),
    UsersModule,
  ],
  controllers: [AppController],
  providers: [AppService],
})
export class AppModule {}
"""

NESTJS_USER_ENTITY_TS = """\
import { Entity, PrimaryGeneratedColumn, Column } from 'typeorm';

@Entity()
export class User {
  @PrimaryGeneratedColumn()
  id: number;

  @Column({ unique: true })
  username: string;

  @Column()
  email: string;

  @Column({ default: true })
  isActive: boolean;
}
"""

NESTJS_TYPEORM_USERS_MODULE_TS = """\
import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { UsersController } from './users.controller';
import { UsersService } from './users.service';
import { User } from './user.entity';

@Module({
  imports: [TypeOrmModule.forFeature([User])],
  controllers: [UsersController],
  providers: [UsersService],
  exports: [UsersService],
})
export class UsersModule {}
"""

NESTJS_TYPEORM_USERS_SERVICE_TS = """\
import { Injectable, NotFoundException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { User } from './user.entity';

@Injectable()
export class UsersService {
  constructor(
    @InjectRepository(User)
    private readonly userRepository: Repository<User>,
  ) {}

  findAll(): Promise<User[]> {
    return this.userRepository.find();
  }

  async findOne(id: number): Promise<User> {
    const user = await this.userRepository.findOneBy({ id });
    if (!user) throw new NotFoundException(`User #${id} not found`);
    return user;
  }

  create(data: Partial<User>): Promise<User> {
    const user = this.userRepository.create(data);
    return this.userRepository.save(user);
  }

  async remove(id: number): Promise<void> {
    await this.userRepository.delete(id);
  }
}
"""

NESTJS_TYPEORM_USERS_CONTROLLER_TS = """\
import {
  Controller,
  Get,
  Post,
  Delete,
  Body,
  Param,
  HttpCode,
  HttpStatus,
} from '@nestjs/common';
import { UsersService } from './users.service';
import { User } from './user.entity';

@Controller('users')
export class UsersController {
  constructor(private readonly usersService: UsersService) {}

  @Get()
  findAll(): Promise<User[]> {
    return this.usersService.findAll();
  }

  @Get(':id')
  findOne(@Param('id') id: string): Promise<User> {
    return this.usersService.findOne(+id);
  }

  @Post()
  @HttpCode(HttpStatus.CREATED)
  create(@Body() body: Partial<User>): Promise<User> {
    return this.usersService.create(body);
  }

  @Delete(':id')
  @HttpCode(HttpStatus.NO_CONTENT)
  remove(@Param('id') id: string): Promise<void> {
    return this.usersService.remove(+id);
  }
}
"""

# ── GraphQL ────────────────────────────────────────────────────────────────────

NESTJS_GRAPHQL_PACKAGE_JSON = """\
{
  "name": "{project_name}",
  "version": "1.0.0",
  "description": "",
  "scripts": {
    "build": "nest build",
    "start": "nest start",
    "start:dev": "nest start --watch",
    "start:prod": "node dist/main",
    "test": "jest",
    "test:cov": "jest --coverage"
  },
  "dependencies": {
    "@apollo/server": "^4.10.4",
    "@as-integrations/express": "^2.0.1",
    "@nestjs/apollo": "^12.1.0",
    "@nestjs/common": "^10.0.0",
    "@nestjs/core": "^10.0.0",
    "@nestjs/graphql": "^12.1.1",
    "@nestjs/platform-express": "^10.0.0",
    "dotenv": "^16.4.5",
    "graphql": "^16.8.1",
    "reflect-metadata": "^0.2.2",
    "rxjs": "^7.8.1"
  },
  "devDependencies": {
    "@nestjs/cli": "^10.0.0",
    "@nestjs/schematics": "^10.0.0",
    "@nestjs/testing": "^10.0.0",
    "@types/jest": "^29.5.12",
    "@types/node": "^20.14.2",
    "jest": "^29.7.0",
    "ts-jest": "^29.1.5",
    "ts-node": "^10.9.2",
    "tslib": "^2.6.3",
    "typescript": "^5.4.5"
  },
  "jest": {
    "moduleFileExtensions": ["js", "json", "ts"],
    "rootDir": "src",
    "testRegex": ".*\\\\.spec\\\\.ts$",
    "transform": {
      "^.+\\\\.(t|j)s$": "ts-jest"
    },
    "collectCoverageFrom": ["**/*.(t|j)s"],
    "coverageDirectory": "../coverage",
    "testEnvironment": "node"
  }
}
"""

NESTJS_GRAPHQL_APP_MODULE_TS = """\
import { Module } from '@nestjs/common';
import { GraphQLModule } from '@nestjs/graphql';
import { ApolloDriver, ApolloDriverConfig } from '@nestjs/apollo';
import { join } from 'path';
import { AppService } from './app.service';
import { ItemsModule } from './items/items.module';

@Module({
  imports: [
    GraphQLModule.forRoot<ApolloDriverConfig>({
      driver: ApolloDriver,
      autoSchemaFile: join(process.cwd(), 'src/schema.gql'),
    }),
    ItemsModule,
  ],
  providers: [AppService],
})
export class AppModule {}
"""

NESTJS_GRAPHQL_ITEM_MODEL_TS = """\
import { ObjectType, Field, Int } from '@nestjs/graphql';

@ObjectType()
export class Item {
  @Field(() => Int)
  id: number;

  @Field()
  name: string;

  @Field({ nullable: true })
  description?: string;
}
"""

NESTJS_GRAPHQL_ITEMS_SERVICE_TS = """\
import { Injectable } from '@nestjs/common';

export interface ItemData {
  id: number;
  name: string;
  description?: string;
}

@Injectable()
export class ItemsService {
  private items: ItemData[] = [];
  private nextId = 1;

  findAll(): ItemData[] {
    return this.items;
  }

  findOne(id: number): ItemData | undefined {
    return this.items.find((i) => i.id === id);
  }

  create(name: string, description?: string): ItemData {
    const item: ItemData = { id: this.nextId++, name, description };
    this.items.push(item);
    return item;
  }
}
"""

NESTJS_GRAPHQL_ITEMS_RESOLVER_TS = """\
import { Resolver, Query, Mutation, Args, Int } from '@nestjs/graphql';
import { Item } from './item.model';
import { ItemsService } from './items.service';

@Resolver(() => Item)
export class ItemsResolver {
  constructor(private readonly itemsService: ItemsService) {}

  @Query(() => [Item])
  items() {
    return this.itemsService.findAll();
  }

  @Query(() => Item, { nullable: true })
  item(@Args('id', { type: () => Int }) id: number) {
    return this.itemsService.findOne(id);
  }

  @Mutation(() => Item)
  createItem(
    @Args('name') name: string,
    @Args('description', { nullable: true }) description?: string,
  ) {
    return this.itemsService.create(name, description);
  }
}
"""

NESTJS_GRAPHQL_ITEMS_MODULE_TS = """\
import { Module } from '@nestjs/common';
import { ItemsResolver } from './items.resolver';
import { ItemsService } from './items.service';

@Module({
  providers: [ItemsResolver, ItemsService],
})
export class ItemsModule {}
"""

# ── Testing ───────────────────────────────────────────────────────────────────

NESTJS_E2E_TEST_TS = """\
import { Test, TestingModule } from '@nestjs/testing';
import { INestApplication } from '@nestjs/common';
import * as request from 'supertest';
import { AppModule } from '../src/app.module';

describe('AppController (e2e)', () => {
  let app: INestApplication;

  beforeEach(async () => {
    const moduleFixture: TestingModule = await Test.createTestingModule({
      imports: [AppModule],
    }).compile();

    app = moduleFixture.createNestApplication();
    await app.init();
  });

  afterEach(async () => {
    await app.close();
  });

  it('GET / should return 200 with message', () => {
    return request(app.getHttpServer())
      .get('/')
      .expect(200)
      .expect((res) => {
        expect(res.body).toHaveProperty('message');
      });
  });

  it('GET /health should return status ok', () => {
    return request(app.getHttpServer())
      .get('/health')
      .expect(200)
      .expect({ status: 'ok' });
  });
});
"""

NESTJS_JEST_E2E_JSON = """\
{
  "moduleFileExtensions": ["js", "json", "ts"],
  "rootDir": ".",
  "testEnvironment": "node",
  "testRegex": ".e2e-spec.ts$",
  "transform": {
    "^.+\\\\.(t|j)s$": "ts-jest"
  }
}
"""

# ── WebSockets ────────────────────────────────────────────────────────────────

NESTJS_WEBSOCKETS_PACKAGE_JSON = """\
{
  "name": "{project_name}",
  "version": "1.0.0",
  "description": "",
  "scripts": {
    "build": "nest build",
    "start": "nest start",
    "start:dev": "nest start --watch",
    "start:prod": "node dist/main",
    "test": "jest"
  },
  "dependencies": {
    "@nestjs/common": "^10.0.0",
    "@nestjs/core": "^10.0.0",
    "@nestjs/platform-express": "^10.0.0",
    "@nestjs/platform-socket.io": "^10.3.10",
    "@nestjs/websockets": "^10.3.10",
    "dotenv": "^16.4.5",
    "reflect-metadata": "^0.2.2",
    "rxjs": "^7.8.1",
    "socket.io": "^4.7.5"
  },
  "devDependencies": {
    "@nestjs/cli": "^10.0.0",
    "@nestjs/schematics": "^10.0.0",
    "@nestjs/testing": "^10.0.0",
    "@types/jest": "^29.5.12",
    "@types/node": "^20.14.2",
    "jest": "^29.7.0",
    "ts-jest": "^29.1.5",
    "ts-node": "^10.9.2",
    "tslib": "^2.6.3",
    "typescript": "^5.4.5"
  },
  "jest": {
    "moduleFileExtensions": ["js", "json", "ts"],
    "rootDir": "src",
    "testRegex": ".*\\\\.spec\\\\.ts$",
    "transform": {
      "^.+\\\\.(t|j)s$": "ts-jest"
    },
    "collectCoverageFrom": ["**/*.(t|j)s"],
    "coverageDirectory": "../coverage",
    "testEnvironment": "node"
  }
}
"""

NESTJS_WEBSOCKETS_APP_MODULE_TS = """\
import { Module } from '@nestjs/common';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { EventsModule } from './events/events.module';

@Module({
  imports: [EventsModule],
  controllers: [AppController],
  providers: [AppService],
})
export class AppModule {}
"""

NESTJS_EVENTS_GATEWAY_TS = """\
import {
  WebSocketGateway,
  WebSocketServer,
  SubscribeMessage,
  MessageBody,
  ConnectedSocket,
  OnGatewayConnection,
  OnGatewayDisconnect,
} from '@nestjs/websockets';
import { Server, Socket } from 'socket.io';

@WebSocketGateway({ cors: { origin: '*' } })
export class EventsGateway implements OnGatewayConnection, OnGatewayDisconnect {
  @WebSocketServer()
  server: Server;

  handleConnection(client: Socket) {
    console.log(`Client connected: ${client.id}`);
    this.server.emit('users', { total: this.server.sockets.sockets.size });
  }

  handleDisconnect(client: Socket) {
    console.log(`Client disconnected: ${client.id}`);
    this.server.emit('users', { total: this.server.sockets.sockets.size });
  }

  @SubscribeMessage('message')
  handleMessage(
    @ConnectedSocket() client: Socket,
    @MessageBody() data: string,
  ): void {
    this.server.emit('message', { from: client.id, data });
  }
}
"""

NESTJS_EVENTS_MODULE_TS = """\
import { Module } from '@nestjs/common';
import { EventsGateway } from './events.gateway';

@Module({
  providers: [EventsGateway],
})
export class EventsModule {}
"""

# ── Battery snippets ──────────────────────────────────────────────────────────

NESTJS_CORS_SETUP = "  app.enableCors();\n"

NESTJS_HELMET_IMPORT = "import helmet from 'helmet';\n"
NESTJS_HELMET_SETUP = "  app.use(helmet());\n"

NESTJS_MONGOOSE_IMPORT = "import { MongooseModule } from '@nestjs/mongoose';\n"
NESTJS_MONGOOSE_MODULE_IMPORT = (
    "    MongooseModule.forRoot(process.env.MONGODB_URI || "
    "'mongodb://localhost:27017/{project_name}'),\n"
)

NESTJS_PRISMA_SERVICE_TS = """\
import { Injectable, OnModuleInit } from '@nestjs/common';
import { PrismaClient } from '@prisma/client';

@Injectable()
export class PrismaService extends PrismaClient implements OnModuleInit {
  async onModuleInit() {
    await this.$connect();
  }
}
"""

NESTJS_PRISMA_MODULE_TS = """\
import { Module, Global } from '@nestjs/common';
import { PrismaService } from './prisma.service';

@Global()
@Module({
  providers: [PrismaService],
  exports: [PrismaService],
})
export class PrismaModule {}
"""

NESTJS_PRISMA_IMPORT = "import { PrismaModule } from './prisma/prisma.module';\n"
NESTJS_PRISMA_MODULE_IMPORT = "    PrismaModule,\n"

NESTJS_PRISMA_SCHEMA = """\
// Learn more: https://pris.ly/d/prisma-schema

generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = env("DB_PROVIDER")
  url      = env("DATABASE_URL")
}
"""

# ── CI/CD ─────────────────────────────────────────────────────────────────────

NESTJS_GITHUB_ACTIONS_WORKFLOW = """\
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

NESTJS_GITLAB_CI = """\
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

NESTJS_BITBUCKET_PIPELINES = """\
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

NESTJS_CIRCLECI_CONFIG = """\
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
MICRONAUT_POM_XML = """\
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.example</groupId>
    <artifactId>{project_name}</artifactId>
    <version>0.1</version>
    <packaging>jar</packaging>
    <parent>
        <groupId>io.micronaut.platform</groupId>
        <artifactId>micronaut-parent</artifactId>
        <version>4.3.2</version>
    </parent>
    <properties>
        <packaging>jar</packaging>
        <jdk.version>21</jdk.version>
        <release.version>21</release.version>
        <micronaut.version>4.3.2</micronaut.version>
        <micronaut.runtime>netty</micronaut.runtime>
        <exec.mainClass>com.example.{package_name}.Application</exec.mainClass>
    </properties>
    <dependencies>
        <dependency>
            <groupId>io.micronaut</groupId>
            <artifactId>micronaut-http-server-netty</artifactId>
            <scope>compile</scope>
        </dependency>
        <dependency>
            <groupId>io.micronaut.serde</groupId>
            <artifactId>micronaut-serde-jackson</artifactId>
            <scope>compile</scope>
        </dependency>
        <dependency>
            <groupId>ch.qos.logback</groupId>
            <artifactId>logback-classic</artifactId>
            <scope>runtime</scope>
        </dependency>
        <dependency>
            <groupId>io.micronaut.test</groupId>
            <artifactId>micronaut-test-junit5</artifactId>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.junit.jupiter</groupId>
            <artifactId>junit-jupiter-api</artifactId>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.junit.jupiter</groupId>
            <artifactId>junit-jupiter-engine</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>
    <build>
        <plugins>
            <plugin>
                <groupId>io.micronaut.maven</groupId>
                <artifactId>micronaut-maven-plugin</artifactId>
            </plugin>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <configuration>
                    <annotationProcessorPaths combine.children="append">
                        <path>
                            <groupId>io.micronaut</groupId>
                            <artifactId>micronaut-http-validation</artifactId>
                            <version>${micronaut.version}</version>
                        </path>
                        <path>
                            <groupId>io.micronaut.serde</groupId>
                            <artifactId>micronaut-serde-processor</artifactId>
                            <version>${micronaut.serde.version}</version>
                        </path>
                    </annotationProcessorPaths>
                </configuration>
            </plugin>
        </plugins>
    </build>
</project>
"""

MICRONAUT_JWT_POM_XML = """\
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.example</groupId>
    <artifactId>{project_name}</artifactId>
    <version>0.1</version>
    <packaging>jar</packaging>
    <parent>
        <groupId>io.micronaut.platform</groupId>
        <artifactId>micronaut-parent</artifactId>
        <version>4.3.2</version>
    </parent>
    <properties>
        <packaging>jar</packaging>
        <jdk.version>21</jdk.version>
        <release.version>21</release.version>
        <micronaut.version>4.3.2</micronaut.version>
        <micronaut.runtime>netty</micronaut.runtime>
        <exec.mainClass>com.example.{package_name}.Application</exec.mainClass>
    </properties>
    <dependencies>
        <dependency>
            <groupId>io.micronaut</groupId>
            <artifactId>micronaut-http-server-netty</artifactId>
            <scope>compile</scope>
        </dependency>
        <dependency>
            <groupId>io.micronaut.serde</groupId>
            <artifactId>micronaut-serde-jackson</artifactId>
            <scope>compile</scope>
        </dependency>
        <dependency>
            <groupId>io.micronaut.security</groupId>
            <artifactId>micronaut-security-jwt</artifactId>
            <scope>compile</scope>
        </dependency>
        <dependency>
            <groupId>ch.qos.logback</groupId>
            <artifactId>logback-classic</artifactId>
            <scope>runtime</scope>
        </dependency>
        <dependency>
            <groupId>io.micronaut.test</groupId>
            <artifactId>micronaut-test-junit5</artifactId>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.junit.jupiter</groupId>
            <artifactId>junit-jupiter-api</artifactId>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.junit.jupiter</groupId>
            <artifactId>junit-jupiter-engine</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>
    <build>
        <plugins>
            <plugin>
                <groupId>io.micronaut.maven</groupId>
                <artifactId>micronaut-maven-plugin</artifactId>
            </plugin>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <configuration>
                    <annotationProcessorPaths combine.children="append">
                        <path>
                            <groupId>io.micronaut</groupId>
                            <artifactId>micronaut-http-validation</artifactId>
                            <version>${micronaut.version}</version>
                        </path>
                        <path>
                            <groupId>io.micronaut.serde</groupId>
                            <artifactId>micronaut-serde-processor</artifactId>
                            <version>${micronaut.serde.version}</version>
                        </path>
                        <path>
                            <groupId>io.micronaut.security</groupId>
                            <artifactId>micronaut-security-annotations</artifactId>
                            <version>${micronaut.security.version}</version>
                        </path>
                    </annotationProcessorPaths>
                </configuration>
            </plugin>
        </plugins>
    </build>
</project>
"""

MICRONAUT_DATA_JPA_POM_XML = """\
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.example</groupId>
    <artifactId>{project_name}</artifactId>
    <version>0.1</version>
    <packaging>jar</packaging>
    <parent>
        <groupId>io.micronaut.platform</groupId>
        <artifactId>micronaut-parent</artifactId>
        <version>4.3.2</version>
    </parent>
    <properties>
        <packaging>jar</packaging>
        <jdk.version>21</jdk.version>
        <release.version>21</release.version>
        <micronaut.version>4.3.2</micronaut.version>
        <micronaut.runtime>netty</micronaut.runtime>
        <exec.mainClass>com.example.{package_name}.Application</exec.mainClass>
    </properties>
    <dependencies>
        <dependency>
            <groupId>io.micronaut</groupId>
            <artifactId>micronaut-http-server-netty</artifactId>
            <scope>compile</scope>
        </dependency>
        <dependency>
            <groupId>io.micronaut.serde</groupId>
            <artifactId>micronaut-serde-jackson</artifactId>
            <scope>compile</scope>
        </dependency>
        <dependency>
            <groupId>io.micronaut.data</groupId>
            <artifactId>micronaut-data-hibernate-jpa</artifactId>
            <scope>compile</scope>
        </dependency>
        <dependency>
            <groupId>io.micronaut.sql</groupId>
            <artifactId>micronaut-jdbc-hikari</artifactId>
            <scope>compile</scope>
        </dependency>
        <dependency>
            <groupId>com.h2database</groupId>
            <artifactId>h2</artifactId>
            <scope>runtime</scope>
        </dependency>
        <dependency>
            <groupId>ch.qos.logback</groupId>
            <artifactId>logback-classic</artifactId>
            <scope>runtime</scope>
        </dependency>
        <dependency>
            <groupId>io.micronaut.test</groupId>
            <artifactId>micronaut-test-junit5</artifactId>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.junit.jupiter</groupId>
            <artifactId>junit-jupiter-api</artifactId>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.junit.jupiter</groupId>
            <artifactId>junit-jupiter-engine</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>
    <build>
        <plugins>
            <plugin>
                <groupId>io.micronaut.maven</groupId>
                <artifactId>micronaut-maven-plugin</artifactId>
            </plugin>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <configuration>
                    <annotationProcessorPaths combine.children="append">
                        <path>
                            <groupId>io.micronaut</groupId>
                            <artifactId>micronaut-http-validation</artifactId>
                            <version>${micronaut.version}</version>
                        </path>
                        <path>
                            <groupId>io.micronaut.serde</groupId>
                            <artifactId>micronaut-serde-processor</artifactId>
                            <version>${micronaut.serde.version}</version>
                        </path>
                        <path>
                            <groupId>io.micronaut.data</groupId>
                            <artifactId>micronaut-data-processor</artifactId>
                            <version>${micronaut.data.version}</version>
                        </path>
                    </annotationProcessorPaths>
                </configuration>
            </plugin>
        </plugins>
    </build>
</project>
"""

MICRONAUT_APPLICATION_JAVA = """\
package com.example.{package_name};

import io.micronaut.runtime.Micronaut;

public class Application {
    public static void main(String[] args) {
        Micronaut.run(Application.class, args);
    }
}
"""

MICRONAUT_HEALTH_CONTROLLER_JAVA = """\
package com.example.{package_name};

import io.micronaut.http.annotation.Controller;
import io.micronaut.http.annotation.Get;
import java.util.Map;

@Controller
public class HealthController {
    @Get("/")
    public Map<String, String> root() {
        return Map.of("message", "Hello from {project_name}!");
    }

    @Get("/health")
    public Map<String, String> health() {
        return Map.of("status", "ok");
    }
}
"""

MICRONAUT_APPLICATION_YML = """\
micronaut:
  application:
    name: {project_name}
  server:
    port: ${PORT:8080}
"""

MICRONAUT_GITIGNORE = """\
target/
.mvn/wrapper/maven-wrapper.jar
.idea/
*.iml
*.class
*.log
.DS_Store
.env
"""

MICRONAUT_ENV = """\
PORT=8080
"""

MICRONAUT_ENV_EXAMPLE = """\
PORT=8080
"""

# ── REST API ──────────────────────────────────────────────────────────────────

MICRONAUT_ITEM_JAVA = """\
package com.example.{package_name}.items;

import io.micronaut.serde.annotation.Serdeable;

@Serdeable
public class Item {
    private Long id;
    private String title;
    private String description;

    public Item() {}

    public Item(Long id, String title, String description) {
        this.id = id;
        this.title = title;
        this.description = description;
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }
    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }
}
"""

MICRONAUT_ITEM_CONTROLLER_JAVA = """\
package com.example.{package_name}.items;

import io.micronaut.http.HttpResponse;
import io.micronaut.http.annotation.*;
import jakarta.inject.Singleton;
import java.util.*;
import java.util.concurrent.atomic.AtomicLong;

@Controller("/api/items")
@Singleton
public class ItemController {
    private final Map<Long, Item> store = new LinkedHashMap<>();
    private final AtomicLong counter = new AtomicLong(1);

    @Get
    public List<Item> list() {
        return new ArrayList<>(store.values());
    }

    @Get("/{id}")
    public HttpResponse<Item> get(Long id) {
        Item item = store.get(id);
        return item != null ? HttpResponse.ok(item) : HttpResponse.notFound();
    }

    @Post
    public Item create(@Body Item item) {
        item.setId(counter.getAndIncrement());
        store.put(item.getId(), item);
        return item;
    }

    @Put("/{id}")
    public HttpResponse<Item> update(Long id, @Body Item item) {
        if (!store.containsKey(id)) return HttpResponse.notFound();
        item.setId(id);
        store.put(id, item);
        return HttpResponse.ok(item);
    }

    @Delete("/{id}")
    public HttpResponse<?> delete(Long id) {
        return store.remove(id) != null
            ? HttpResponse.noContent()
            : HttpResponse.notFound();
    }
}
"""

# ── JWT AUTH ──────────────────────────────────────────────────────────────────

MICRONAUT_AUTH_REQUEST_JAVA = """\
package com.example.{package_name}.auth;

import io.micronaut.serde.annotation.Serdeable;

@Serdeable
public record AuthRequest(String username, String password) {}
"""

MICRONAUT_AUTH_RESPONSE_JAVA = """\
package com.example.{package_name}.auth;

import io.micronaut.serde.annotation.Serdeable;

@Serdeable
public record AuthResponse(String token) {}
"""

MICRONAUT_USER_DETAILS_PROVIDER_JAVA = """\
package com.example.{package_name}.auth;

import io.micronaut.http.HttpRequest;
import io.micronaut.security.authentication.*;
import jakarta.inject.Singleton;
import org.reactivestreams.Publisher;
import reactor.core.publisher.Mono;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

@Singleton
public class UserDetailsProvider implements AuthenticationProvider<HttpRequest<?>> {
    private final Map<String, String> users = new ConcurrentHashMap<>();

    public void register(String username, String password) {
        if (users.containsKey(username)) throw new IllegalArgumentException("Username taken");
        users.put(username, password);
    }

    @Override
    public Publisher<AuthenticationResponse> authenticate(
            HttpRequest<?> httpRequest, AuthenticationRequest<?, ?> authRequest) {
        String username = authRequest.getIdentity().toString();
        String password = authRequest.getSecret().toString();
        String stored = users.get(username);
        if (stored != null && stored.equals(password)) {
            return Mono.just(AuthenticationResponse.success(username));
        }
        return Mono.just(AuthenticationResponse.failure(AuthenticationFailureReason.CREDENTIALS_DO_NOT_MATCH));
    }
}
"""

MICRONAUT_AUTH_CONTROLLER_JAVA = """\
package com.example.{package_name}.auth;

import io.micronaut.http.HttpResponse;
import io.micronaut.http.annotation.*;
import io.micronaut.security.annotation.Secured;
import io.micronaut.security.rules.SecurityRule;
import io.micronaut.security.token.jwt.generator.JwtTokenGenerator;
import jakarta.inject.Inject;
import java.util.Map;
import java.util.Optional;

@Controller("/api/auth")
@Secured(SecurityRule.IS_ANONYMOUS)
public class AuthController {
    @Inject
    private UserDetailsProvider userDetailsProvider;

    @Inject
    private JwtTokenGenerator tokenGenerator;

    @Post("/register")
    public HttpResponse<AuthResponse> register(@Body AuthRequest request) {
        try {
            userDetailsProvider.register(request.username(), request.password());
            Optional<String> token = tokenGenerator.generateToken(
                Map.of("sub", request.username()));
            return token.map(t -> HttpResponse.ok(new AuthResponse(t)))
                .orElse(HttpResponse.serverError());
        } catch (IllegalArgumentException e) {
            return HttpResponse.status(io.micronaut.http.HttpStatus.CONFLICT);
        }
    }
}
"""

MICRONAUT_JWT_APPLICATION_YML = """\
micronaut:
  application:
    name: {project_name}
  server:
    port: ${PORT:8080}
  security:
    enabled: true
    token:
      jwt:
        enabled: true
        signatures:
          secret:
            generator:
              secret: ${JWT_SECRET:pleaseChangeThisSecretForAProductionApplication}
"""

MICRONAUT_JWT_ENV = """\
PORT=8080
JWT_SECRET=pleaseChangeThisSecretForAProductionApplication
"""

MICRONAUT_JWT_ENV_EXAMPLE = """\
PORT=8080
JWT_SECRET=your-256-bit-secret-here
"""

# ── DOCKER ────────────────────────────────────────────────────────────────────

MICRONAUT_DOCKERFILE = """\
FROM maven:3.9-eclipse-temurin-21-alpine AS build
WORKDIR /app
COPY pom.xml .
RUN mvn dependency:resolve -q
COPY src ./src
RUN mvn package -DskipTests -q

FROM eclipse-temurin:21-jre-alpine
WORKDIR /app
COPY --from=build /app/target/{project_name}-0.1.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
"""

MICRONAUT_DOCKER_COMPOSE_YML = """\
services:
  app:
    build: .
    ports:
      - "8080:8080"
    environment:
      - PORT=8080
    env_file:
      - .env
"""

MICRONAUT_DOCKERIGNORE = """\
target/
.git/
.env
*.md
.idea/
*.iml
"""

# ── DATA JPA ──────────────────────────────────────────────────────────────────

MICRONAUT_USER_ENTITY_JAVA = """\
package com.example.{package_name}.users;

import io.micronaut.serde.annotation.Serdeable;
import jakarta.persistence.*;

@Serdeable
@Entity
@Table(name = "users")
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String name;

    @Column(unique = true, nullable = false)
    private String email;

    public User() {}

    public User(String name, String email) {
        this.name = name;
        this.email = email;
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }
}
"""

MICRONAUT_USER_REPOSITORY_JAVA = """\
package com.example.{package_name}.users;

import io.micronaut.data.annotation.Repository;
import io.micronaut.data.repository.CrudRepository;
import java.util.Optional;

@Repository
public interface UserRepository extends CrudRepository<User, Long> {
    Optional<User> findByEmail(String email);
}
"""

MICRONAUT_USER_SERVICE_JAVA = """\
package com.example.{package_name}.users;

import jakarta.inject.Singleton;
import java.util.List;

@Singleton
public class UserService {
    private final UserRepository repository;

    public UserService(UserRepository repository) {
        this.repository = repository;
    }

    public List<User> findAll() {
        return (List<User>) repository.findAll();
    }

    public User findById(Long id) {
        return repository.findById(id)
            .orElseThrow(() -> new IllegalArgumentException("User not found: " + id));
    }

    public User create(User user) { return repository.save(user); }

    public User update(Long id, User incoming) {
        User user = findById(id);
        user.setName(incoming.getName());
        user.setEmail(incoming.getEmail());
        return repository.update(user);
    }

    public void delete(Long id) { repository.deleteById(id); }
}
"""

MICRONAUT_USER_CONTROLLER_JAVA = """\
package com.example.{package_name}.users;

import io.micronaut.http.HttpResponse;
import io.micronaut.http.annotation.*;
import java.util.List;

@Controller("/api/users")
public class UserController {
    private final UserService service;

    public UserController(UserService service) {
        this.service = service;
    }

    @Get
    public List<User> list() { return service.findAll(); }

    @Get("/{id}")
    public User get(Long id) { return service.findById(id); }

    @Post
    public User create(@Body User user) { return service.create(user); }

    @Put("/{id}")
    public User update(Long id, @Body User user) { return service.update(id, user); }

    @Delete("/{id}")
    public HttpResponse<?> delete(Long id) {
        service.delete(id);
        return HttpResponse.noContent();
    }
}
"""

MICRONAUT_DATA_JPA_APPLICATION_YML = """\
micronaut:
  application:
    name: {project_name}
  server:
    port: ${PORT:8080}

datasources:
  default:
    url: jdbc:h2:mem:devDb;LOCK_TIMEOUT=10000;DB_CLOSE_ON_EXIT=FALSE
    driverClassName: org.h2.Driver
    username: sa
    password: ''
    schema-generate: CREATE_DROP
    dialect: H2
"""

# ── TESTING ───────────────────────────────────────────────────────────────────

MICRONAUT_HEALTH_CONTROLLER_TEST_JAVA = """\
package com.example.{package_name};

import io.micronaut.http.HttpResponse;
import io.micronaut.http.client.HttpClient;
import io.micronaut.http.client.annotation.Client;
import io.micronaut.test.extensions.junit5.annotation.MicronautTest;
import jakarta.inject.Inject;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

@MicronautTest
class HealthControllerTest {
    @Inject
    @Client("/")
    HttpClient client;

    @Test
    void healthEndpointReturnsOk() {
        HttpResponse<?> response = client.toBlocking().exchange("/health");
        assertEquals(200, response.getStatus().getCode());
    }

    @Test
    void rootEndpointReturns200() {
        HttpResponse<?> response = client.toBlocking().exchange("/");
        assertEquals(200, response.getStatus().getCode());
    }
}
"""

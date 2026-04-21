QUARKUS_POM_XML = """\
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.example</groupId>
    <artifactId>{project_name}</artifactId>
    <version>1.0.0-SNAPSHOT</version>
    <properties>
        <compiler-plugin.version>3.12.1</compiler-plugin.version>
        <maven.compiler.release>21</maven.compiler.release>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
        <quarkus.platform.artifact-id>quarkus-bom</quarkus.platform.artifact-id>
        <quarkus.platform.group-id>io.quarkus.platform</quarkus.platform.group-id>
        <quarkus.platform.version>3.8.2</quarkus.platform.version>
    </properties>
    <dependencyManagement>
        <dependencies>
            <dependency>
                <groupId>${quarkus.platform.group-id}</groupId>
                <artifactId>${quarkus.platform.artifact-id}</artifactId>
                <version>${quarkus.platform.version}</version>
                <type>pom</type>
                <scope>import</scope>
            </dependency>
        </dependencies>
    </dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>io.quarkus</groupId>
            <artifactId>quarkus-rest</artifactId>
        </dependency>
        <dependency>
            <groupId>io.quarkus</groupId>
            <artifactId>quarkus-rest-jackson</artifactId>
        </dependency>
        <dependency>
            <groupId>io.quarkus</groupId>
            <artifactId>quarkus-arc</artifactId>
        </dependency>
        <dependency>
            <groupId>io.quarkus</groupId>
            <artifactId>quarkus-junit5</artifactId>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>io.rest-assured</groupId>
            <artifactId>rest-assured</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>
    <build>
        <plugins>
            <plugin>
                <groupId>${quarkus.platform.group-id}</groupId>
                <artifactId>quarkus-maven-plugin</artifactId>
                <version>${quarkus.platform.version}</version>
                <extensions>true</extensions>
                <executions>
                    <execution>
                        <goals>
                            <goal>build</goal>
                            <goal>generate-code</goal>
                            <goal>generate-code-tests</goal>
                        </goals>
                    </execution>
                </executions>
            </plugin>
            <plugin>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>${compiler-plugin.version}</version>
            </plugin>
        </plugins>
    </build>
</project>
"""

QUARKUS_JWT_POM_XML = """\
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.example</groupId>
    <artifactId>{project_name}</artifactId>
    <version>1.0.0-SNAPSHOT</version>
    <properties>
        <compiler-plugin.version>3.12.1</compiler-plugin.version>
        <maven.compiler.release>21</maven.compiler.release>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
        <quarkus.platform.artifact-id>quarkus-bom</quarkus.platform.artifact-id>
        <quarkus.platform.group-id>io.quarkus.platform</quarkus.platform.group-id>
        <quarkus.platform.version>3.8.2</quarkus.platform.version>
    </properties>
    <dependencyManagement>
        <dependencies>
            <dependency>
                <groupId>${quarkus.platform.group-id}</groupId>
                <artifactId>${quarkus.platform.artifact-id}</artifactId>
                <version>${quarkus.platform.version}</version>
                <type>pom</type>
                <scope>import</scope>
            </dependency>
        </dependencies>
    </dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>io.quarkus</groupId>
            <artifactId>quarkus-rest</artifactId>
        </dependency>
        <dependency>
            <groupId>io.quarkus</groupId>
            <artifactId>quarkus-rest-jackson</artifactId>
        </dependency>
        <dependency>
            <groupId>io.quarkus</groupId>
            <artifactId>quarkus-arc</artifactId>
        </dependency>
        <dependency>
            <groupId>io.quarkus</groupId>
            <artifactId>quarkus-smallrye-jwt</artifactId>
        </dependency>
        <dependency>
            <groupId>io.quarkus</groupId>
            <artifactId>quarkus-smallrye-jwt-build</artifactId>
        </dependency>
        <dependency>
            <groupId>io.quarkus</groupId>
            <artifactId>quarkus-junit5</artifactId>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>io.rest-assured</groupId>
            <artifactId>rest-assured</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>
    <build>
        <plugins>
            <plugin>
                <groupId>${quarkus.platform.group-id}</groupId>
                <artifactId>quarkus-maven-plugin</artifactId>
                <version>${quarkus.platform.version}</version>
                <extensions>true</extensions>
                <executions>
                    <execution>
                        <goals>
                            <goal>build</goal>
                            <goal>generate-code</goal>
                            <goal>generate-code-tests</goal>
                        </goals>
                    </execution>
                </executions>
            </plugin>
            <plugin>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>${compiler-plugin.version}</version>
            </plugin>
        </plugins>
    </build>
</project>
"""

QUARKUS_PANACHE_POM_XML = """\
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.example</groupId>
    <artifactId>{project_name}</artifactId>
    <version>1.0.0-SNAPSHOT</version>
    <properties>
        <compiler-plugin.version>3.12.1</compiler-plugin.version>
        <maven.compiler.release>21</maven.compiler.release>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
        <quarkus.platform.artifact-id>quarkus-bom</quarkus.platform.artifact-id>
        <quarkus.platform.group-id>io.quarkus.platform</quarkus.platform.group-id>
        <quarkus.platform.version>3.8.2</quarkus.platform.version>
    </properties>
    <dependencyManagement>
        <dependencies>
            <dependency>
                <groupId>${quarkus.platform.group-id}</groupId>
                <artifactId>${quarkus.platform.artifact-id}</artifactId>
                <version>${quarkus.platform.version}</version>
                <type>pom</type>
                <scope>import</scope>
            </dependency>
        </dependencies>
    </dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>io.quarkus</groupId>
            <artifactId>quarkus-rest</artifactId>
        </dependency>
        <dependency>
            <groupId>io.quarkus</groupId>
            <artifactId>quarkus-rest-jackson</artifactId>
        </dependency>
        <dependency>
            <groupId>io.quarkus</groupId>
            <artifactId>quarkus-hibernate-orm-panache</artifactId>
        </dependency>
        <dependency>
            <groupId>io.quarkus</groupId>
            <artifactId>quarkus-jdbc-h2</artifactId>
        </dependency>
        <dependency>
            <groupId>io.quarkus</groupId>
            <artifactId>quarkus-arc</artifactId>
        </dependency>
        <dependency>
            <groupId>io.quarkus</groupId>
            <artifactId>quarkus-junit5</artifactId>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>io.rest-assured</groupId>
            <artifactId>rest-assured</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>
    <build>
        <plugins>
            <plugin>
                <groupId>${quarkus.platform.group-id}</groupId>
                <artifactId>quarkus-maven-plugin</artifactId>
                <version>${quarkus.platform.version}</version>
                <extensions>true</extensions>
                <executions>
                    <execution>
                        <goals>
                            <goal>build</goal>
                            <goal>generate-code</goal>
                            <goal>generate-code-tests</goal>
                        </goals>
                    </execution>
                </executions>
            </plugin>
            <plugin>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>${compiler-plugin.version}</version>
            </plugin>
        </plugins>
    </build>
</project>
"""

QUARKUS_GREETING_RESOURCE_JAVA = """\
package com.example.{package_name};

import jakarta.ws.rs.GET;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.MediaType;
import java.util.Map;

@Path("/")
public class GreetingResource {
    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public Map<String, String> hello() {
        return Map.of("message", "Hello from {project_name}!");
    }

    @GET
    @Path("/health")
    @Produces(MediaType.APPLICATION_JSON)
    public Map<String, String> health() {
        return Map.of("status", "ok");
    }
}
"""

QUARKUS_APPLICATION_PROPERTIES = """\
quarkus.http.port=${PORT:8080}
quarkus.application.name={project_name}
"""

QUARKUS_GITIGNORE = """\
target/
.mvn/wrapper/maven-wrapper.jar
.idea/
*.iml
*.class
*.log
.DS_Store
.env
"""

QUARKUS_ENV = """\
PORT=8080
"""

QUARKUS_ENV_EXAMPLE = """\
PORT=8080
"""

# ── REST API ──────────────────────────────────────────────────────────────────

QUARKUS_ITEM_JAVA = """\
package com.example.{package_name}.items;

public class Item {
    public Long id;
    public String title;
    public String description;

    public Item() {}

    public Item(Long id, String title, String description) {
        this.id = id;
        this.title = title;
        this.description = description;
    }
}
"""

QUARKUS_ITEM_RESOURCE_JAVA = """\
package com.example.{package_name}.items;

import jakarta.enterprise.context.ApplicationScoped;
import jakarta.ws.rs.*;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;
import java.util.*;
import java.util.concurrent.atomic.AtomicLong;

@Path("/api/items")
@Produces(MediaType.APPLICATION_JSON)
@Consumes(MediaType.APPLICATION_JSON)
@ApplicationScoped
public class ItemResource {
    private final Map<Long, Item> store = new LinkedHashMap<>();
    private final AtomicLong counter = new AtomicLong(1);

    @GET
    public List<Item> list() {
        return new ArrayList<>(store.values());
    }

    @GET
    @Path("/{id}")
    public Response getById(@PathParam("id") Long id) {
        Item item = store.get(id);
        return item != null ? Response.ok(item).build() : Response.status(404).build();
    }

    @POST
    public Response create(Item item) {
        item.id = counter.getAndIncrement();
        store.put(item.id, item);
        return Response.status(201).entity(item).build();
    }

    @PUT
    @Path("/{id}")
    public Response update(@PathParam("id") Long id, Item item) {
        if (!store.containsKey(id)) return Response.status(404).build();
        item.id = id;
        store.put(id, item);
        return Response.ok(item).build();
    }

    @DELETE
    @Path("/{id}")
    public Response delete(@PathParam("id") Long id) {
        return store.remove(id) != null
            ? Response.noContent().build()
            : Response.status(404).build();
    }
}
"""

# ── JWT AUTH ──────────────────────────────────────────────────────────────────

QUARKUS_AUTH_REQUEST_JAVA = """\
package com.example.{package_name}.auth;

public record AuthRequest(String username, String password) {}
"""

QUARKUS_AUTH_RESPONSE_JAVA = """\
package com.example.{package_name}.auth;

public record AuthResponse(String token) {}
"""

QUARKUS_AUTH_RESOURCE_JAVA = """\
package com.example.{package_name}.auth;

import io.smallrye.jwt.build.Jwt;
import jakarta.annotation.security.PermitAll;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.ws.rs.*;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

@Path("/api/auth")
@ApplicationScoped
@Produces(MediaType.APPLICATION_JSON)
@Consumes(MediaType.APPLICATION_JSON)
public class AuthResource {
    private final Map<String, String> users = new ConcurrentHashMap<>();

    @POST
    @Path("/register")
    @PermitAll
    public Response register(AuthRequest request) {
        if (users.containsKey(request.username())) {
            return Response.status(409).entity(Map.of("error", "Username taken")).build();
        }
        users.put(request.username(), request.password());
        return Response.ok(new AuthResponse(buildToken(request.username()))).build();
    }

    @POST
    @Path("/login")
    @PermitAll
    public Response login(AuthRequest request) {
        String stored = users.get(request.username());
        if (stored == null || !stored.equals(request.password())) {
            return Response.status(401).entity(Map.of("error", "Invalid credentials")).build();
        }
        return Response.ok(new AuthResponse(buildToken(request.username()))).build();
    }

    private String buildToken(String username) {
        return Jwt.issuer("https://example.com/issuer")
            .upn(username)
            .groups("user")
            .expiresIn(86400)
            .sign();
    }
}
"""

QUARKUS_JWT_APPLICATION_PROPERTIES = """\
quarkus.http.port=${PORT:8080}
quarkus.application.name={project_name}
mp.jwt.verify.publickey.location=META-INF/resources/publicKey.pem
mp.jwt.verify.issuer=https://example.com/issuer
smallrye.jwt.sign.key.location=privateKey.pem
"""

QUARKUS_JWT_ENV = """\
PORT=8080
"""

QUARKUS_JWT_ENV_EXAMPLE = """\
PORT=8080
"""

# ── DOCKER ────────────────────────────────────────────────────────────────────

QUARKUS_DOCKERFILE_JVM = """\
FROM maven:3.9-eclipse-temurin-21-alpine AS build
WORKDIR /app
COPY pom.xml .
RUN mvn dependency:resolve -q
COPY src ./src
RUN mvn package -DskipTests -q

FROM eclipse-temurin:21-jre-alpine
WORKDIR /app
COPY --from=build /app/target/quarkus-app/lib/ /deployments/lib/
COPY --from=build /app/target/quarkus-app/*.jar /deployments/
COPY --from=build /app/target/quarkus-app/app/ /deployments/app/
COPY --from=build /app/target/quarkus-app/quarkus/ /deployments/quarkus/
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "/deployments/quarkus-run.jar"]
"""

QUARKUS_DOCKER_COMPOSE_YML = """\
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

QUARKUS_DOCKERIGNORE = """\
target/
.git/
.env
*.md
.idea/
*.iml
"""

# ── HIBERNATE PANACHE ─────────────────────────────────────────────────────────

QUARKUS_PANACHE_ENTITY_JAVA = """\
package com.example.{package_name}.users;

import io.quarkus.hibernate.orm.panache.PanacheEntity;
import jakarta.persistence.Entity;
import jakarta.persistence.Table;

@Entity
@Table(name = "users")
public class User extends PanacheEntity {
    public String name;
    public String email;
}
"""

QUARKUS_PANACHE_RESOURCE_JAVA = """\
package com.example.{package_name}.users;

import jakarta.enterprise.context.ApplicationScoped;
import jakarta.transaction.Transactional;
import jakarta.ws.rs.*;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;
import java.util.List;

@Path("/api/users")
@Produces(MediaType.APPLICATION_JSON)
@Consumes(MediaType.APPLICATION_JSON)
@ApplicationScoped
public class UserResource {
    @GET
    public List<User> list() {
        return User.listAll();
    }

    @GET
    @Path("/{id}")
    public Response getById(@PathParam("id") Long id) {
        User user = User.findById(id);
        return user != null ? Response.ok(user).build() : Response.status(404).build();
    }

    @POST
    @Transactional
    public Response create(User user) {
        user.persist();
        return Response.status(201).entity(user).build();
    }

    @PUT
    @Path("/{id}")
    @Transactional
    public Response update(@PathParam("id") Long id, User incoming) {
        User user = User.findById(id);
        if (user == null) return Response.status(404).build();
        user.name = incoming.name;
        user.email = incoming.email;
        return Response.ok(user).build();
    }

    @DELETE
    @Path("/{id}")
    @Transactional
    public Response delete(@PathParam("id") Long id) {
        return User.deleteById(id)
            ? Response.noContent().build()
            : Response.status(404).build();
    }
}
"""

QUARKUS_PANACHE_APPLICATION_PROPERTIES = """\
quarkus.http.port=${PORT:8080}
quarkus.application.name={project_name}
quarkus.datasource.db-kind=h2
quarkus.datasource.jdbc.url=jdbc:h2:mem:testdb;DB_CLOSE_DELAY=-1
quarkus.hibernate-orm.database.generation=drop-and-create
quarkus.hibernate-orm.log.sql=false
"""

# ── TESTING ───────────────────────────────────────────────────────────────────

QUARKUS_GREETING_RESOURCE_TEST_JAVA = """\
package com.example.{package_name};

import io.quarkus.test.junit.QuarkusTest;
import org.junit.jupiter.api.Test;

import static io.restassured.RestAssured.given;
import static org.hamcrest.CoreMatchers.*;

@QuarkusTest
class GreetingResourceTest {
    @Test
    void testHealthEndpoint() {
        given()
            .when().get("/health")
            .then()
            .statusCode(200)
            .body("status", is("ok"));
    }

    @Test
    void testRootEndpoint() {
        given()
            .when().get("/")
            .then()
            .statusCode(200);
    }
}
"""

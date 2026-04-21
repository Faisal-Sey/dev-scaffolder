ECHO_GO_MOD = """\
module {project_name}

go 1.22

require (
\tgithub.com/joho/godotenv v1.5.1
\tgithub.com/labstack/echo/v4 v4.12.0
)
"""

ECHO_JWT_GO_MOD = """\
module {project_name}

go 1.22

require (
\tgithub.com/golang-jwt/jwt/v5 v5.2.1
\tgithub.com/joho/godotenv v1.5.1
\tgithub.com/labstack/echo/v4 v4.12.0
)
"""

ECHO_GORM_GO_MOD = """\
module {project_name}

go 1.22

require (
\tgithub.com/joho/godotenv v1.5.1
\tgithub.com/labstack/echo/v4 v4.12.0
\tgorm.io/driver/sqlite v1.5.5
\tgorm.io/gorm v1.25.10
)
"""

ECHO_MAIN_GO = """\
package main

import (
\t"net/http"
\t"os"

\t"github.com/joho/godotenv"
\t"github.com/labstack/echo/v4"
\t"github.com/labstack/echo/v4/middleware"
)

func main() {
\t_ = godotenv.Load()

\te := echo.New()
\te.Use(middleware.Logger())
\te.Use(middleware.Recover())

\te.GET("/", func(c echo.Context) error {
\t\treturn c.JSON(http.StatusOK, map[string]string{"message": "Hello, World!"})
\t})
\te.GET("/health", func(c echo.Context) error {
\t\treturn c.JSON(http.StatusOK, map[string]string{"status": "ok"})
\t})

\tport := os.Getenv("PORT")
\tif port == "" {
\t\tport = "8080"
\t}
\te.Logger.Fatal(e.Start(":" + port))
}
"""

ECHO_REST_API_MAIN_GO = """\
package main

import (
\t"net/http"
\t"os"
\t"strconv"
\t"sync"
\t"sync/atomic"

\t"github.com/joho/godotenv"
\t"github.com/labstack/echo/v4"
\t"github.com/labstack/echo/v4/middleware"
)

type Item struct {
\tID          int64  `json:"id"`
\tTitle       string `json:"title"`
\tDescription string `json:"description"`
}

type CreateItemRequest struct {
\tTitle       string `json:"title"`
\tDescription string `json:"description"`
}

type AppState struct {
\tmu      sync.RWMutex
\titems   map[int64]Item
\tcounter atomic.Int64
}

func main() {
\t_ = godotenv.Load()

\tstate := &AppState{items: make(map[int64]Item)}

\te := echo.New()
\te.Use(middleware.Logger())
\te.Use(middleware.Recover())

\tg := e.Group("/api")

\tg.GET("/items", func(c echo.Context) error {
\t\tstate.mu.RLock()
\t\tdefer state.mu.RUnlock()
\t\tlist := make([]Item, 0, len(state.items))
\t\tfor _, v := range state.items {
\t\t\tlist = append(list, v)
\t\t}
\t\treturn c.JSON(http.StatusOK, list)
\t})

\tg.GET("/items/:id", func(c echo.Context) error {
\t\tid, err := strconv.ParseInt(c.Param("id"), 10, 64)
\t\tif err != nil {
\t\t\treturn c.JSON(http.StatusBadRequest, map[string]string{"error": "invalid id"})
\t\t}
\t\tstate.mu.RLock()
\t\titem, ok := state.items[id]
\t\tstate.mu.RUnlock()
\t\tif !ok {
\t\t\treturn c.JSON(http.StatusNotFound, map[string]string{"error": "not found"})
\t\t}
\t\treturn c.JSON(http.StatusOK, item)
\t})

\tg.POST("/items", func(c echo.Context) error {
\t\tvar req CreateItemRequest
\t\tif err := c.Bind(&req); err != nil {
\t\t\treturn c.JSON(http.StatusBadRequest, map[string]string{"error": err.Error()})
\t\t}
\t\tid := state.counter.Add(1)
\t\titem := Item{ID: id, Title: req.Title, Description: req.Description}
\t\tstate.mu.Lock()
\t\tstate.items[id] = item
\t\tstate.mu.Unlock()
\t\treturn c.JSON(http.StatusCreated, item)
\t})

\tg.PUT("/items/:id", func(c echo.Context) error {
\t\tid, err := strconv.ParseInt(c.Param("id"), 10, 64)
\t\tif err != nil {
\t\t\treturn c.JSON(http.StatusBadRequest, map[string]string{"error": "invalid id"})
\t\t}
\t\tvar req CreateItemRequest
\t\tif err := c.Bind(&req); err != nil {
\t\t\treturn c.JSON(http.StatusBadRequest, map[string]string{"error": err.Error()})
\t\t}
\t\tstate.mu.Lock()
\t\tdefer state.mu.Unlock()
\t\tif _, ok := state.items[id]; !ok {
\t\t\treturn c.JSON(http.StatusNotFound, map[string]string{"error": "not found"})
\t\t}
\t\titem := Item{ID: id, Title: req.Title, Description: req.Description}
\t\tstate.items[id] = item
\t\treturn c.JSON(http.StatusOK, item)
\t})

\tg.DELETE("/items/:id", func(c echo.Context) error {
\t\tid, err := strconv.ParseInt(c.Param("id"), 10, 64)
\t\tif err != nil {
\t\t\treturn c.JSON(http.StatusBadRequest, map[string]string{"error": "invalid id"})
\t\t}
\t\tstate.mu.Lock()
\t\tdefer state.mu.Unlock()
\t\tif _, ok := state.items[id]; !ok {
\t\t\treturn c.JSON(http.StatusNotFound, map[string]string{"error": "not found"})
\t\t}
\t\tdelete(state.items, id)
\t\treturn c.NoContent(http.StatusNoContent)
\t})

\tport := os.Getenv("PORT")
\tif port == "" {
\t\tport = "8080"
\t}
\te.Logger.Fatal(e.Start(":" + port))
}
"""

ECHO_JWT_AUTH_MAIN_GO = """\
package main

import (
\t"net/http"
\t"os"
\t"strings"
\t"sync"
\t"time"

\t"github.com/golang-jwt/jwt/v5"
\t"github.com/joho/godotenv"
\t"github.com/labstack/echo/v4"
\t"github.com/labstack/echo/v4/middleware"
)

type User struct {
\tUsername string `json:"username"`
\tPassword string `json:"password"`
}

type Claims struct {
\tUsername string `json:"username"`
\tjwt.RegisteredClaims
}

var (
\tusers   = make(map[string]string)
\tusersMu sync.RWMutex
)

func main() {
\t_ = godotenv.Load()

\tsecret := os.Getenv("JWT_SECRET")
\tif secret == "" {
\t\tsecret = "changeme"
\t}

\te := echo.New()
\te.Use(middleware.Logger())
\te.Use(middleware.Recover())

\te.POST("/api/auth/register", func(c echo.Context) error {
\t\tvar u User
\t\tif err := c.Bind(&u); err != nil {
\t\t\treturn c.JSON(http.StatusBadRequest, map[string]string{"error": err.Error()})
\t\t}
\t\tusersMu.Lock()
\t\tdefer usersMu.Unlock()
\t\tif _, exists := users[u.Username]; exists {
\t\t\treturn c.JSON(http.StatusConflict, map[string]string{"error": "user already exists"})
\t\t}
\t\tusers[u.Username] = u.Password
\t\treturn c.JSON(http.StatusCreated, map[string]string{"message": "registered"})
\t})

\te.POST("/api/auth/login", func(c echo.Context) error {
\t\tvar u User
\t\tif err := c.Bind(&u); err != nil {
\t\t\treturn c.JSON(http.StatusBadRequest, map[string]string{"error": err.Error()})
\t\t}
\t\tusersMu.RLock()
\t\tstoredPwd, ok := users[u.Username]
\t\tusersMu.RUnlock()
\t\tif !ok || storedPwd != u.Password {
\t\t\treturn c.JSON(http.StatusUnauthorized, map[string]string{"error": "invalid credentials"})
\t\t}
\t\tclaims := &Claims{
\t\t\tUsername: u.Username,
\t\t\tRegisteredClaims: jwt.RegisteredClaims{
\t\t\t\tExpiresAt: jwt.NewNumericDate(time.Now().Add(24 * time.Hour)),
\t\t\t},
\t\t}
\t\ttoken := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
\t\tsigned, err := token.SignedString([]byte(secret))
\t\tif err != nil {
\t\t\treturn c.JSON(http.StatusInternalServerError, map[string]string{"error": "token error"})
\t\t}
\t\treturn c.JSON(http.StatusOK, map[string]string{"token": signed})
\t})

\tauthMiddleware := func(next echo.HandlerFunc) echo.HandlerFunc {
\t\treturn func(c echo.Context) error {
\t\t\tauth := c.Request().Header.Get("Authorization")
\t\t\tif !strings.HasPrefix(auth, "Bearer ") {
\t\t\t\treturn c.JSON(http.StatusUnauthorized, map[string]string{"error": "missing token"})
\t\t\t}
\t\t\ttokenStr := strings.TrimPrefix(auth, "Bearer ")
\t\t\tclaims := &Claims{}
\t\t\tparsed, err := jwt.ParseWithClaims(tokenStr, claims, func(t *jwt.Token) (interface{}, error) {
\t\t\t\treturn []byte(secret), nil
\t\t\t})
\t\t\tif err != nil || !parsed.Valid {
\t\t\t\treturn c.JSON(http.StatusUnauthorized, map[string]string{"error": "invalid token"})
\t\t\t}
\t\t\tc.Set("username", claims.Username)
\t\t\treturn next(c)
\t\t}
\t}

\te.GET("/api/protected", func(c echo.Context) error {
\t\treturn c.JSON(http.StatusOK, map[string]string{"message": "welcome " + c.Get("username").(string)})
\t}, authMiddleware)

\tport := os.Getenv("PORT")
\tif port == "" {
\t\tport = "8080"
\t}
\te.Logger.Fatal(e.Start(":" + port))
}
"""

ECHO_GORM_MAIN_GO = """\
package main

import (
\t"net/http"
\t"os"
\t"strconv"

\t"github.com/joho/godotenv"
\t"github.com/labstack/echo/v4"
\t"github.com/labstack/echo/v4/middleware"
\t"gorm.io/driver/sqlite"
\t"gorm.io/gorm"
)

type Item struct {
\tID          uint   `gorm:"primaryKey;autoIncrement" json:"id"`
\tTitle       string `json:"title"`
\tDescription string `json:"description"`
}

type CreateItemRequest struct {
\tTitle       string `json:"title"`
\tDescription string `json:"description"`
}

func main() {
\t_ = godotenv.Load()

\tdsn := os.Getenv("DATABASE_URL")
\tif dsn == "" {
\t\tdsn = "file::memory:?cache=shared"
\t}
\tdb, err := gorm.Open(sqlite.Open(dsn), &gorm.Config{})
\tif err != nil {
\t\tpanic("failed to connect to database: " + err.Error())
\t}
\tif err := db.AutoMigrate(&Item{}); err != nil {
\t\tpanic("auto-migrate failed: " + err.Error())
\t}

\te := echo.New()
\te.Use(middleware.Logger())
\te.Use(middleware.Recover())

\tg := e.Group("/api")

\tg.GET("/items", func(c echo.Context) error {
\t\tvar items []Item
\t\tdb.Find(&items)
\t\treturn c.JSON(http.StatusOK, items)
\t})

\tg.GET("/items/:id", func(c echo.Context) error {
\t\tid, err := strconv.ParseUint(c.Param("id"), 10, 64)
\t\tif err != nil {
\t\t\treturn c.JSON(http.StatusBadRequest, map[string]string{"error": "invalid id"})
\t\t}
\t\tvar item Item
\t\tif res := db.First(&item, id); res.Error != nil {
\t\t\treturn c.JSON(http.StatusNotFound, map[string]string{"error": "not found"})
\t\t}
\t\treturn c.JSON(http.StatusOK, item)
\t})

\tg.POST("/items", func(c echo.Context) error {
\t\tvar req CreateItemRequest
\t\tif err := c.Bind(&req); err != nil {
\t\t\treturn c.JSON(http.StatusBadRequest, map[string]string{"error": err.Error()})
\t\t}
\t\titem := Item{Title: req.Title, Description: req.Description}
\t\tdb.Create(&item)
\t\treturn c.JSON(http.StatusCreated, item)
\t})

\tg.PUT("/items/:id", func(c echo.Context) error {
\t\tid, err := strconv.ParseUint(c.Param("id"), 10, 64)
\t\tif err != nil {
\t\t\treturn c.JSON(http.StatusBadRequest, map[string]string{"error": "invalid id"})
\t\t}
\t\tvar item Item
\t\tif res := db.First(&item, id); res.Error != nil {
\t\t\treturn c.JSON(http.StatusNotFound, map[string]string{"error": "not found"})
\t\t}
\t\tvar req CreateItemRequest
\t\tif err := c.Bind(&req); err != nil {
\t\t\treturn c.JSON(http.StatusBadRequest, map[string]string{"error": err.Error()})
\t\t}
\t\titem.Title = req.Title
\t\titem.Description = req.Description
\t\tdb.Save(&item)
\t\treturn c.JSON(http.StatusOK, item)
\t})

\tg.DELETE("/items/:id", func(c echo.Context) error {
\t\tid, err := strconv.ParseUint(c.Param("id"), 10, 64)
\t\tif err != nil {
\t\t\treturn c.JSON(http.StatusBadRequest, map[string]string{"error": "invalid id"})
\t\t}
\t\tvar item Item
\t\tif res := db.First(&item, id); res.Error != nil {
\t\t\treturn c.JSON(http.StatusNotFound, map[string]string{"error": "not found"})
\t\t}
\t\tdb.Delete(&item)
\t\treturn c.NoContent(http.StatusNoContent)
\t})

\tport := os.Getenv("PORT")
\tif port == "" {
\t\tport = "8080"
\t}
\te.Logger.Fatal(e.Start(":" + port))
}
"""

ECHO_TESTING_MAIN_GO = """\
package main

import (
\t"net/http"
\t"os"

\t"github.com/joho/godotenv"
\t"github.com/labstack/echo/v4"
\t"github.com/labstack/echo/v4/middleware"
)

func buildServer() *echo.Echo {
\te := echo.New()
\te.Use(middleware.Recover())

\te.GET("/", func(c echo.Context) error {
\t\treturn c.JSON(http.StatusOK, map[string]string{"message": "Hello, World!"})
\t})
\te.GET("/health", func(c echo.Context) error {
\t\treturn c.JSON(http.StatusOK, map[string]string{"status": "ok"})
\t})
\treturn e
}

func main() {
\t_ = godotenv.Load()
\te := buildServer()
\te.Use(middleware.Logger())
\tport := os.Getenv("PORT")
\tif port == "" {
\t\tport = "8080"
\t}
\te.Logger.Fatal(e.Start(":" + port))
}
"""

ECHO_TESTING_MAIN_TEST_GO = """\
package main

import (
\t"net/http"
\t"net/http/httptest"
\t"testing"
)

func TestHealthEndpoint(t *testing.T) {
\te := buildServer()
\treq := httptest.NewRequest(http.MethodGet, "/health", nil)
\trec := httptest.NewRecorder()
\te.ServeHTTP(rec, req)
\tif rec.Code != http.StatusOK {
\t\tt.Fatalf("expected 200, got %d", rec.Code)
\t}
}

func TestRootEndpoint(t *testing.T) {
\te := buildServer()
\treq := httptest.NewRequest(http.MethodGet, "/", nil)
\trec := httptest.NewRecorder()
\te.ServeHTTP(rec, req)
\tif rec.Code != http.StatusOK {
\t\tt.Fatalf("expected 200, got %d", rec.Code)
\t}
}
"""

ECHO_DOCKERFILE = """\
FROM golang:1.22-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o server .

FROM alpine:3.19
RUN apk --no-cache add ca-certificates
WORKDIR /root/
COPY --from=builder /app/server .
EXPOSE 8080
CMD ["./server"]
"""

ECHO_DOCKER_COMPOSE_YML = """\
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8080:8080"
    environment:
      - PORT=8080
    restart: unless-stopped
"""

ECHO_DOCKERIGNORE = """\
/server
*.exe
*.test
*.out
vendor/
.env
.git/
"""

ECHO_GITIGNORE = """\
/server
*.exe
*.test
*.out
vendor/
.env
"""

ECHO_ENV = """\
PORT=8080
"""

ECHO_ENV_EXAMPLE = """\
PORT=8080
"""

ECHO_JWT_ENV = """\
PORT=8080
JWT_SECRET=changeme
"""

ECHO_JWT_ENV_EXAMPLE = """\
PORT=8080
JWT_SECRET=changeme
"""

ECHO_GORM_ENV = """\
PORT=8080
DATABASE_URL=file::memory:?cache=shared
"""

ECHO_GORM_ENV_EXAMPLE = """\
PORT=8080
DATABASE_URL=file::memory:?cache=shared
"""

GIN_GO_MOD = """\
module {project_name}

go 1.22

require (
\tgithub.com/gin-gonic/gin v1.10.0
\tgithub.com/joho/godotenv v1.5.1
)
"""

GIN_JWT_GO_MOD = """\
module {project_name}

go 1.22

require (
\tgithub.com/gin-gonic/gin v1.10.0
\tgithub.com/golang-jwt/jwt/v5 v5.2.1
\tgithub.com/joho/godotenv v1.5.1
)
"""

GIN_GORM_GO_MOD = """\
module {project_name}

go 1.22

require (
\tgithub.com/gin-gonic/gin v1.10.0
\tgithub.com/joho/godotenv v1.5.1
\tgorm.io/driver/sqlite v1.5.5
\tgorm.io/gorm v1.25.10
)
"""

GIN_MAIN_GO = """\
package main

import (
\t"net/http"
\t"os"

\t"github.com/gin-gonic/gin"
\t"github.com/joho/godotenv"
)

func main() {
\t_ = godotenv.Load()

\tgin.SetMode(gin.ReleaseMode)
\tr := gin.Default()

\tr.GET("/", func(c *gin.Context) {
\t\tc.JSON(http.StatusOK, gin.H{"message": "Hello, World!"})
\t})
\tr.GET("/health", func(c *gin.Context) {
\t\tc.JSON(http.StatusOK, gin.H{"status": "ok"})
\t})

\tport := os.Getenv("PORT")
\tif port == "" {
\t\tport = "8080"
\t}
\tr.Run(":" + port)
}
"""

GIN_REST_API_MAIN_GO = """\
package main

import (
\t"net/http"
\t"os"
\t"strconv"
\t"sync"
\t"sync/atomic"

\t"github.com/gin-gonic/gin"
\t"github.com/joho/godotenv"
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

\tgin.SetMode(gin.ReleaseMode)
\tr := gin.Default()

\tg := r.Group("/api")

\tg.GET("/items", func(c *gin.Context) {
\t\tstate.mu.RLock()
\t\tdefer state.mu.RUnlock()
\t\tlist := make([]Item, 0, len(state.items))
\t\tfor _, v := range state.items {
\t\t\tlist = append(list, v)
\t\t}
\t\tc.JSON(http.StatusOK, list)
\t})

\tg.GET("/items/:id", func(c *gin.Context) {
\t\tid, err := strconv.ParseInt(c.Param("id"), 10, 64)
\t\tif err != nil {
\t\t\tc.JSON(http.StatusBadRequest, gin.H{"error": "invalid id"})
\t\t\treturn
\t\t}
\t\tstate.mu.RLock()
\t\titem, ok := state.items[id]
\t\tstate.mu.RUnlock()
\t\tif !ok {
\t\t\tc.JSON(http.StatusNotFound, gin.H{"error": "not found"})
\t\t\treturn
\t\t}
\t\tc.JSON(http.StatusOK, item)
\t})

\tg.POST("/items", func(c *gin.Context) {
\t\tvar req CreateItemRequest
\t\tif err := c.ShouldBindJSON(&req); err != nil {
\t\t\tc.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
\t\t\treturn
\t\t}
\t\tid := state.counter.Add(1)
\t\titem := Item{ID: id, Title: req.Title, Description: req.Description}
\t\tstate.mu.Lock()
\t\tstate.items[id] = item
\t\tstate.mu.Unlock()
\t\tc.JSON(http.StatusCreated, item)
\t})

\tg.PUT("/items/:id", func(c *gin.Context) {
\t\tid, err := strconv.ParseInt(c.Param("id"), 10, 64)
\t\tif err != nil {
\t\t\tc.JSON(http.StatusBadRequest, gin.H{"error": "invalid id"})
\t\t\treturn
\t\t}
\t\tvar req CreateItemRequest
\t\tif err := c.ShouldBindJSON(&req); err != nil {
\t\t\tc.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
\t\t\treturn
\t\t}
\t\tstate.mu.Lock()
\t\tdefer state.mu.Unlock()
\t\tif _, ok := state.items[id]; !ok {
\t\t\tc.JSON(http.StatusNotFound, gin.H{"error": "not found"})
\t\t\treturn
\t\t}
\t\titem := Item{ID: id, Title: req.Title, Description: req.Description}
\t\tstate.items[id] = item
\t\tc.JSON(http.StatusOK, item)
\t})

\tg.DELETE("/items/:id", func(c *gin.Context) {
\t\tid, err := strconv.ParseInt(c.Param("id"), 10, 64)
\t\tif err != nil {
\t\t\tc.JSON(http.StatusBadRequest, gin.H{"error": "invalid id"})
\t\t\treturn
\t\t}
\t\tstate.mu.Lock()
\t\tdefer state.mu.Unlock()
\t\tif _, ok := state.items[id]; !ok {
\t\t\tc.JSON(http.StatusNotFound, gin.H{"error": "not found"})
\t\t\treturn
\t\t}
\t\tdelete(state.items, id)
\t\tc.Status(http.StatusNoContent)
\t})

\tport := os.Getenv("PORT")
\tif port == "" {
\t\tport = "8080"
\t}
\tr.Run(":" + port)
}
"""

GIN_JWT_AUTH_MAIN_GO = """\
package main

import (
\t"net/http"
\t"os"
\t"strings"
\t"sync"
\t"time"

\t"github.com/gin-gonic/gin"
\t"github.com/golang-jwt/jwt/v5"
\t"github.com/joho/godotenv"
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

\tgin.SetMode(gin.ReleaseMode)
\tr := gin.Default()

\tauth := r.Group("/api/auth")
\tauth.POST("/register", func(c *gin.Context) {
\t\tvar u User
\t\tif err := c.ShouldBindJSON(&u); err != nil {
\t\t\tc.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
\t\t\treturn
\t\t}
\t\tusersMu.Lock()
\t\tdefer usersMu.Unlock()
\t\tif _, exists := users[u.Username]; exists {
\t\t\tc.JSON(http.StatusConflict, gin.H{"error": "user already exists"})
\t\t\treturn
\t\t}
\t\tusers[u.Username] = u.Password
\t\tc.JSON(http.StatusCreated, gin.H{"message": "registered"})
\t})

\tauth.POST("/login", func(c *gin.Context) {
\t\tvar u User
\t\tif err := c.ShouldBindJSON(&u); err != nil {
\t\t\tc.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
\t\t\treturn
\t\t}
\t\tusersMu.RLock()
\t\tstoredPwd, ok := users[u.Username]
\t\tusersMu.RUnlock()
\t\tif !ok || storedPwd != u.Password {
\t\t\tc.JSON(http.StatusUnauthorized, gin.H{"error": "invalid credentials"})
\t\t\treturn
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
\t\t\tc.JSON(http.StatusInternalServerError, gin.H{"error": "token error"})
\t\t\treturn
\t\t}
\t\tc.JSON(http.StatusOK, gin.H{"token": signed})
\t})

\tauthMiddleware := func(c *gin.Context) {
\t\tauthorization := c.GetHeader("Authorization")
\t\tif !strings.HasPrefix(authorization, "Bearer ") {
\t\t\tc.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "missing token"})
\t\t\treturn
\t\t}
\t\ttokenStr := strings.TrimPrefix(authorization, "Bearer ")
\t\tclaims := &Claims{}
\t\tparsed, err := jwt.ParseWithClaims(tokenStr, claims, func(t *jwt.Token) (interface{}, error) {
\t\t\treturn []byte(secret), nil
\t\t})
\t\tif err != nil || !parsed.Valid {
\t\t\tc.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "invalid token"})
\t\t\treturn
\t\t}
\t\tc.Set("username", claims.Username)
\t\tc.Next()
\t}

\tr.GET("/api/protected", authMiddleware, func(c *gin.Context) {
\t\tusername, _ := c.Get("username")
\t\tc.JSON(http.StatusOK, gin.H{"message": "welcome " + username.(string)})
\t})

\tport := os.Getenv("PORT")
\tif port == "" {
\t\tport = "8080"
\t}
\tr.Run(":" + port)
}
"""

GIN_GORM_MAIN_GO = """\
package main

import (
\t"net/http"
\t"os"
\t"strconv"

\t"github.com/gin-gonic/gin"
\t"github.com/joho/godotenv"
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

\tgin.SetMode(gin.ReleaseMode)
\tr := gin.Default()

\tg := r.Group("/api")

\tg.GET("/items", func(c *gin.Context) {
\t\tvar items []Item
\t\tdb.Find(&items)
\t\tc.JSON(http.StatusOK, items)
\t})

\tg.GET("/items/:id", func(c *gin.Context) {
\t\tid, err := strconv.ParseUint(c.Param("id"), 10, 64)
\t\tif err != nil {
\t\t\tc.JSON(http.StatusBadRequest, gin.H{"error": "invalid id"})
\t\t\treturn
\t\t}
\t\tvar item Item
\t\tif res := db.First(&item, id); res.Error != nil {
\t\t\tc.JSON(http.StatusNotFound, gin.H{"error": "not found"})
\t\t\treturn
\t\t}
\t\tc.JSON(http.StatusOK, item)
\t})

\tg.POST("/items", func(c *gin.Context) {
\t\tvar req CreateItemRequest
\t\tif err := c.ShouldBindJSON(&req); err != nil {
\t\t\tc.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
\t\t\treturn
\t\t}
\t\titem := Item{Title: req.Title, Description: req.Description}
\t\tdb.Create(&item)
\t\tc.JSON(http.StatusCreated, item)
\t})

\tg.PUT("/items/:id", func(c *gin.Context) {
\t\tid, err := strconv.ParseUint(c.Param("id"), 10, 64)
\t\tif err != nil {
\t\t\tc.JSON(http.StatusBadRequest, gin.H{"error": "invalid id"})
\t\t\treturn
\t\t}
\t\tvar item Item
\t\tif res := db.First(&item, id); res.Error != nil {
\t\t\tc.JSON(http.StatusNotFound, gin.H{"error": "not found"})
\t\t\treturn
\t\t}
\t\tvar req CreateItemRequest
\t\tif err := c.ShouldBindJSON(&req); err != nil {
\t\t\tc.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
\t\t\treturn
\t\t}
\t\titem.Title = req.Title
\t\titem.Description = req.Description
\t\tdb.Save(&item)
\t\tc.JSON(http.StatusOK, item)
\t})

\tg.DELETE("/items/:id", func(c *gin.Context) {
\t\tid, err := strconv.ParseUint(c.Param("id"), 10, 64)
\t\tif err != nil {
\t\t\tc.JSON(http.StatusBadRequest, gin.H{"error": "invalid id"})
\t\t\treturn
\t\t}
\t\tvar item Item
\t\tif res := db.First(&item, id); res.Error != nil {
\t\t\tc.JSON(http.StatusNotFound, gin.H{"error": "not found"})
\t\t\treturn
\t\t}
\t\tdb.Delete(&item)
\t\tc.Status(http.StatusNoContent)
\t})

\tport := os.Getenv("PORT")
\tif port == "" {
\t\tport = "8080"
\t}
\tr.Run(":" + port)
}
"""

GIN_TESTING_MAIN_GO = """\
package main

import (
\t"net/http"
\t"os"

\t"github.com/gin-gonic/gin"
\t"github.com/joho/godotenv"
)

func buildRouter() *gin.Engine {
\tr := gin.New()
\tr.Use(gin.Recovery())

\tr.GET("/", func(c *gin.Context) {
\t\tc.JSON(http.StatusOK, gin.H{"message": "Hello, World!"})
\t})
\tr.GET("/health", func(c *gin.Context) {
\t\tc.JSON(http.StatusOK, gin.H{"status": "ok"})
\t})
\treturn r
}

func main() {
\t_ = godotenv.Load()
\tgin.SetMode(gin.ReleaseMode)
\tr := buildRouter()
\tr.Use(gin.Logger())
\tport := os.Getenv("PORT")
\tif port == "" {
\t\tport = "8080"
\t}
\tr.Run(":" + port)
}
"""

GIN_TESTING_MAIN_TEST_GO = """\
package main

import (
\t"net/http"
\t"net/http/httptest"
\t"testing"

\t"github.com/gin-gonic/gin"
)

func init() {
\tgin.SetMode(gin.TestMode)
}

func TestHealthEndpoint(t *testing.T) {
\tr := buildRouter()
\treq := httptest.NewRequest(http.MethodGet, "/health", nil)
\trec := httptest.NewRecorder()
\tr.ServeHTTP(rec, req)
\tif rec.Code != http.StatusOK {
\t\tt.Fatalf("expected 200, got %d", rec.Code)
\t}
}

func TestRootEndpoint(t *testing.T) {
\tr := buildRouter()
\treq := httptest.NewRequest(http.MethodGet, "/", nil)
\trec := httptest.NewRecorder()
\tr.ServeHTTP(rec, req)
\tif rec.Code != http.StatusOK {
\t\tt.Fatalf("expected 200, got %d", rec.Code)
\t}
}
"""

GIN_DOCKERFILE = """\
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

GIN_DOCKER_COMPOSE_YML = """\
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

GIN_DOCKERIGNORE = """\
/server
*.exe
*.test
*.out
vendor/
.env
.git/
"""

GIN_GITIGNORE = """\
/server
*.exe
*.test
*.out
vendor/
.env
"""

GIN_ENV = """\
PORT=8080
"""

GIN_ENV_EXAMPLE = """\
PORT=8080
"""

GIN_JWT_ENV = """\
PORT=8080
JWT_SECRET=changeme
"""

GIN_JWT_ENV_EXAMPLE = """\
PORT=8080
JWT_SECRET=changeme
"""

GIN_GORM_ENV = """\
PORT=8080
DATABASE_URL=file::memory:?cache=shared
"""

GIN_GORM_ENV_EXAMPLE = """\
PORT=8080
DATABASE_URL=file::memory:?cache=shared
"""

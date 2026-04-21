# ── CARGO MANIFESTS ───────────────────────────────────────────────────────────

ACTIX_CARGO_TOML = """\
[package]
name = "{project_name}"
version = "0.1.0"
edition = "2021"

[dependencies]
actix-web = "4"
tokio = { version = "1", features = ["full"] }
serde = { version = "1", features = ["derive"] }
serde_json = "1"
env_logger = "0.11"
dotenv = "0.15"
"""

ACTIX_JWT_AUTH_CARGO_TOML = """\
[package]
name = "{project_name}"
version = "0.1.0"
edition = "2021"

[dependencies]
actix-web = "4"
tokio = { version = "1", features = ["full"] }
serde = { version = "1", features = ["derive"] }
serde_json = "1"
jsonwebtoken = "9"
env_logger = "0.11"
dotenv = "0.15"
"""

ACTIX_SQLX_CARGO_TOML = """\
[package]
name = "{project_name}"
version = "0.1.0"
edition = "2021"

[dependencies]
actix-web = "4"
tokio = { version = "1", features = ["full"] }
serde = { version = "1", features = ["derive"] }
serde_json = "1"
sqlx = { version = "0.7", features = ["runtime-tokio-rustls", "sqlite", "macros"] }
env_logger = "0.11"
dotenv = "0.15"
"""

# ── MAIN.RS FILES ─────────────────────────────────────────────────────────────

ACTIX_MAIN_RS = """\
use actix_web::{get, App, HttpResponse, HttpServer, Responder};
use serde_json::json;

#[get("/")]
async fn index() -> impl Responder {
    HttpResponse::Ok().json(json!({ "message": "Hello from {project_name}!" }))
}

#[get("/health")]
async fn health() -> impl Responder {
    HttpResponse::Ok().json(json!({ "status": "ok" }))
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    dotenv::dotenv().ok();
    env_logger::init_from_env(env_logger::Env::default().default_filter_or("info"));

    let port: u16 = std::env::var("PORT")
        .unwrap_or_else(|_| "8080".to_string())
        .parse()
        .expect("PORT must be a number");

    println!("Server running at http://localhost:{port}");

    HttpServer::new(|| App::new().service(index).service(health))
        .bind(("0.0.0.0", port))?
        .run()
        .await
}
"""

ACTIX_REST_API_MAIN_RS = """\
use actix_web::{delete, get, post, put, web, App, HttpResponse, HttpServer, Responder};
use serde::{Deserialize, Serialize};
use serde_json::json;
use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use std::sync::atomic::{AtomicU64, Ordering};

#[derive(Debug, Clone, Serialize, Deserialize)]
struct Item {
    #[serde(skip_deserializing)]
    id: u64,
    title: String,
    description: Option<String>,
}

struct AppState {
    items: Mutex<HashMap<u64, Item>>,
    counter: AtomicU64,
}

#[get("/")]
async fn index() -> impl Responder {
    HttpResponse::Ok().json(json!({ "message": "Hello from {project_name}!" }))
}

#[get("/health")]
async fn health() -> impl Responder {
    HttpResponse::Ok().json(json!({ "status": "ok" }))
}

#[get("/api/items")]
async fn list_items(state: web::Data<Arc<AppState>>) -> impl Responder {
    let items = state.items.lock().unwrap();
    HttpResponse::Ok().json(items.values().collect::<Vec<_>>())
}

#[get("/api/items/{id}")]
async fn get_item(state: web::Data<Arc<AppState>>, path: web::Path<u64>) -> impl Responder {
    let id = path.into_inner();
    let items = state.items.lock().unwrap();
    match items.get(&id) {
        Some(item) => HttpResponse::Ok().json(item),
        None => HttpResponse::NotFound().json(json!({ "error": "Not found" })),
    }
}

#[post("/api/items")]
async fn create_item(state: web::Data<Arc<AppState>>, body: web::Json<Item>) -> impl Responder {
    let id = state.counter.fetch_add(1, Ordering::SeqCst);
    let mut item = body.into_inner();
    item.id = id;
    state.items.lock().unwrap().insert(id, item.clone());
    HttpResponse::Ok().json(item)
}

#[put("/api/items/{id}")]
async fn update_item(
    state: web::Data<Arc<AppState>>,
    path: web::Path<u64>,
    body: web::Json<Item>,
) -> impl Responder {
    let id = path.into_inner();
    let mut items = state.items.lock().unwrap();
    if !items.contains_key(&id) {
        return HttpResponse::NotFound().json(json!({ "error": "Not found" }));
    }
    let mut item = body.into_inner();
    item.id = id;
    items.insert(id, item.clone());
    HttpResponse::Ok().json(item)
}

#[delete("/api/items/{id}")]
async fn delete_item(state: web::Data<Arc<AppState>>, path: web::Path<u64>) -> impl Responder {
    let id = path.into_inner();
    let mut items = state.items.lock().unwrap();
    if items.remove(&id).is_some() {
        HttpResponse::NoContent().finish()
    } else {
        HttpResponse::NotFound().json(json!({ "error": "Not found" }))
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    dotenv::dotenv().ok();
    env_logger::init_from_env(env_logger::Env::default().default_filter_or("info"));

    let port: u16 = std::env::var("PORT")
        .unwrap_or_else(|_| "8080".to_string())
        .parse()
        .expect("PORT must be a number");

    let state = Arc::new(AppState {
        items: Mutex::new(HashMap::new()),
        counter: AtomicU64::new(1),
    });

    println!("Server running at http://localhost:{port}");

    HttpServer::new(move || {
        App::new()
            .app_data(web::Data::new(state.clone()))
            .service(index)
            .service(health)
            .service(list_items)
            .service(get_item)
            .service(create_item)
            .service(update_item)
            .service(delete_item)
    })
    .bind(("0.0.0.0", port))?
    .run()
    .await
}
"""

ACTIX_JWT_AUTH_MAIN_RS = """\
use actix_web::{get, post, web, App, HttpRequest, HttpResponse, HttpServer, Responder};
use actix_web::http::header::AUTHORIZATION;
use jsonwebtoken::{decode, encode, DecodingKey, EncodingKey, Header, Validation};
use serde::{Deserialize, Serialize};
use serde_json::json;
use std::collections::HashMap;
use std::sync::Mutex;
use std::time::{SystemTime, UNIX_EPOCH};

#[derive(Deserialize)]
struct AuthRequest {
    username: String,
    password: String,
}

#[derive(Serialize, Deserialize)]
struct Claims {
    sub: String,
    exp: usize,
}

struct AppState {
    users: Mutex<HashMap<String, String>>,
    secret: String,
}

fn unix_now_plus(secs: u64) -> usize {
    (SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs() + secs) as usize
}

fn make_token(secret: &str, username: &str) -> String {
    let claims = Claims { sub: username.to_string(), exp: unix_now_plus(86400) };
    encode(&Header::default(), &claims, &EncodingKey::from_secret(secret.as_bytes())).unwrap()
}

fn verify_token(req: &HttpRequest, secret: &str) -> Option<Claims> {
    req.headers()
        .get(AUTHORIZATION)
        .and_then(|v| v.to_str().ok())
        .and_then(|v| v.strip_prefix("Bearer "))
        .and_then(|t| {
            decode::<Claims>(t, &DecodingKey::from_secret(secret.as_bytes()), &Validation::default()).ok()
        })
        .map(|d| d.claims)
}

#[get("/health")]
async fn health() -> impl Responder {
    HttpResponse::Ok().json(json!({ "status": "ok" }))
}

#[post("/api/auth/register")]
async fn register(state: web::Data<AppState>, body: web::Json<AuthRequest>) -> impl Responder {
    let mut users = state.users.lock().unwrap();
    if users.contains_key(&body.username) {
        return HttpResponse::Conflict().json(json!({ "error": "Username taken" }));
    }
    users.insert(body.username.clone(), body.password.clone());
    HttpResponse::Ok().json(json!({ "token": make_token(&state.secret, &body.username) }))
}

#[post("/api/auth/login")]
async fn login(state: web::Data<AppState>, body: web::Json<AuthRequest>) -> impl Responder {
    let users = state.users.lock().unwrap();
    match users.get(&body.username) {
        Some(pw) if pw == &body.password => {
            HttpResponse::Ok().json(json!({ "token": make_token(&state.secret, &body.username) }))
        }
        _ => HttpResponse::Unauthorized().json(json!({ "error": "Invalid credentials" })),
    }
}

#[get("/api/protected")]
async fn protected(state: web::Data<AppState>, req: HttpRequest) -> impl Responder {
    match verify_token(&req, &state.secret) {
        Some(claims) => {
            HttpResponse::Ok().json(json!({ "message": format!("Hello, {}!", claims.sub) }))
        }
        None => HttpResponse::Unauthorized().json(json!({ "error": "Unauthorized" })),
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    dotenv::dotenv().ok();
    env_logger::init_from_env(env_logger::Env::default().default_filter_or("info"));

    let port: u16 = std::env::var("PORT")
        .unwrap_or_else(|_| "8080".to_string())
        .parse()
        .expect("PORT must be a number");

    let secret = std::env::var("JWT_SECRET")
        .unwrap_or_else(|_| "change-me-in-production".to_string());

    let state = web::Data::new(AppState {
        users: Mutex::new(HashMap::new()),
        secret,
    });

    println!("Server running at http://localhost:{port}");

    HttpServer::new(move || {
        App::new()
            .app_data(state.clone())
            .service(health)
            .service(register)
            .service(login)
            .service(protected)
    })
    .bind(("0.0.0.0", port))?
    .run()
    .await
}
"""

ACTIX_SQLX_MAIN_RS = """\
use actix_web::{delete, get, post, put, web, App, HttpResponse, HttpServer, Responder};
use serde::{Deserialize, Serialize};
use serde_json::json;
use sqlx::SqlitePool;

#[derive(Debug, Serialize, sqlx::FromRow)]
struct Item {
    id: i64,
    title: String,
    description: Option<String>,
}

#[derive(Deserialize)]
struct ItemInput {
    title: String,
    description: Option<String>,
}

async fn setup_db(pool: &SqlitePool) {
    sqlx::query(
        "CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT
        )",
    )
    .execute(pool)
    .await
    .expect("Failed to create items table");
}

#[get("/")]
async fn index() -> impl Responder {
    HttpResponse::Ok().json(json!({ "message": "Hello from {project_name}!" }))
}

#[get("/health")]
async fn health() -> impl Responder {
    HttpResponse::Ok().json(json!({ "status": "ok" }))
}

#[get("/api/items")]
async fn list_items(pool: web::Data<SqlitePool>) -> impl Responder {
    match sqlx::query_as::<_, Item>("SELECT id, title, description FROM items")
        .fetch_all(pool.get_ref())
        .await
    {
        Ok(items) => HttpResponse::Ok().json(items),
        Err(e) => HttpResponse::InternalServerError().json(json!({ "error": e.to_string() })),
    }
}

#[get("/api/items/{id}")]
async fn get_item(pool: web::Data<SqlitePool>, path: web::Path<i64>) -> impl Responder {
    let id = path.into_inner();
    match sqlx::query_as::<_, Item>("SELECT id, title, description FROM items WHERE id = ?")
        .bind(id)
        .fetch_optional(pool.get_ref())
        .await
    {
        Ok(Some(item)) => HttpResponse::Ok().json(item),
        Ok(None) => HttpResponse::NotFound().json(json!({ "error": "Not found" })),
        Err(e) => HttpResponse::InternalServerError().json(json!({ "error": e.to_string() })),
    }
}

#[post("/api/items")]
async fn create_item(pool: web::Data<SqlitePool>, body: web::Json<ItemInput>) -> impl Responder {
    let result = sqlx::query("INSERT INTO items (title, description) VALUES (?, ?)")
        .bind(&body.title)
        .bind(&body.description)
        .execute(pool.get_ref())
        .await;

    match result {
        Ok(r) => {
            let id = r.last_insert_rowid();
            match sqlx::query_as::<_, Item>(
                "SELECT id, title, description FROM items WHERE id = ?",
            )
            .bind(id)
            .fetch_one(pool.get_ref())
            .await
            {
                Ok(item) => HttpResponse::Ok().json(item),
                Err(e) => HttpResponse::InternalServerError().json(json!({ "error": e.to_string() })),
            }
        }
        Err(e) => HttpResponse::InternalServerError().json(json!({ "error": e.to_string() })),
    }
}

#[put("/api/items/{id}")]
async fn update_item(
    pool: web::Data<SqlitePool>,
    path: web::Path<i64>,
    body: web::Json<ItemInput>,
) -> impl Responder {
    let id = path.into_inner();
    match sqlx::query("UPDATE items SET title = ?, description = ? WHERE id = ?")
        .bind(&body.title)
        .bind(&body.description)
        .bind(id)
        .execute(pool.get_ref())
        .await
    {
        Ok(r) if r.rows_affected() == 0 => {
            HttpResponse::NotFound().json(json!({ "error": "Not found" }))
        }
        Ok(_) => {
            match sqlx::query_as::<_, Item>(
                "SELECT id, title, description FROM items WHERE id = ?",
            )
            .bind(id)
            .fetch_one(pool.get_ref())
            .await
            {
                Ok(item) => HttpResponse::Ok().json(item),
                Err(e) => HttpResponse::InternalServerError().json(json!({ "error": e.to_string() })),
            }
        }
        Err(e) => HttpResponse::InternalServerError().json(json!({ "error": e.to_string() })),
    }
}

#[delete("/api/items/{id}")]
async fn delete_item(pool: web::Data<SqlitePool>, path: web::Path<i64>) -> impl Responder {
    let id = path.into_inner();
    match sqlx::query("DELETE FROM items WHERE id = ?")
        .bind(id)
        .execute(pool.get_ref())
        .await
    {
        Ok(r) if r.rows_affected() == 0 => {
            HttpResponse::NotFound().json(json!({ "error": "Not found" }))
        }
        Ok(_) => HttpResponse::NoContent().finish(),
        Err(e) => HttpResponse::InternalServerError().json(json!({ "error": e.to_string() })),
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    dotenv::dotenv().ok();
    env_logger::init_from_env(env_logger::Env::default().default_filter_or("info"));

    let database_url = std::env::var("DATABASE_URL")
        .unwrap_or_else(|_| "sqlite::memory:".to_string());
    let pool = SqlitePool::connect(&database_url)
        .await
        .expect("Failed to connect to database");
    setup_db(&pool).await;

    let port: u16 = std::env::var("PORT")
        .unwrap_or_else(|_| "8080".to_string())
        .parse()
        .expect("PORT must be a number");

    println!("Server running at http://localhost:{port}");

    let pool_data = web::Data::new(pool);

    HttpServer::new(move || {
        App::new()
            .app_data(pool_data.clone())
            .service(index)
            .service(health)
            .service(list_items)
            .service(get_item)
            .service(create_item)
            .service(update_item)
            .service(delete_item)
    })
    .bind(("0.0.0.0", port))?
    .run()
    .await
}
"""

ACTIX_TESTING_MAIN_RS = """\
use actix_web::{get, App, HttpResponse, HttpServer, Responder};
use serde_json::json;

#[get("/")]
async fn index() -> impl Responder {
    HttpResponse::Ok().json(json!({ "message": "Hello from {project_name}!" }))
}

#[get("/health")]
async fn health() -> impl Responder {
    HttpResponse::Ok().json(json!({ "status": "ok" }))
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    dotenv::dotenv().ok();
    env_logger::init_from_env(env_logger::Env::default().default_filter_or("info"));

    let port: u16 = std::env::var("PORT")
        .unwrap_or_else(|_| "8080".to_string())
        .parse()
        .expect("PORT must be a number");

    println!("Server running at http://localhost:{port}");

    HttpServer::new(|| App::new().service(index).service(health))
        .bind(("0.0.0.0", port))?
        .run()
        .await
}

#[cfg(test)]
mod tests {
    use super::*;
    use actix_web::test;

    #[actix_web::test]
    async fn test_health_returns_ok() {
        let app = test::init_service(App::new().service(health)).await;
        let req = test::TestRequest::get().uri("/health").to_request();
        let resp = test::call_service(&app, req).await;
        assert_eq!(resp.status(), 200);
    }

    #[actix_web::test]
    async fn test_index_returns_message() {
        let app = test::init_service(App::new().service(index)).await;
        let req = test::TestRequest::get().uri("/").to_request();
        let resp = test::call_service(&app, req).await;
        assert_eq!(resp.status(), 200);
        let body: serde_json::Value = test::read_body_json(resp).await;
        assert!(body["message"].is_string());
    }
}
"""

# ── DOCKER ────────────────────────────────────────────────────────────────────

ACTIX_DOCKERFILE = """\
FROM rust:1.76 AS builder
WORKDIR /app
COPY Cargo.toml ./
RUN mkdir src && echo 'fn main() {}' > src/main.rs && \
    cargo build --release && \
    rm -rf src
COPY src ./src
RUN cargo build --release

FROM debian:bookworm-slim AS runtime
RUN apt-get update && apt-get install -y ca-certificates && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY --from=builder /app/target/release/{project_name} ./server
EXPOSE 8080
ENV PORT=8080
CMD ["./server"]
"""

ACTIX_DOCKER_COMPOSE_YML = """\
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

ACTIX_DOCKERIGNORE = """\
target/
.git/
.env
*.md
"""

# ── MISC ──────────────────────────────────────────────────────────────────────

ACTIX_GITIGNORE = """\
/target
.env
"""

ACTIX_ENV = """\
PORT=8080
"""

ACTIX_ENV_EXAMPLE = """\
PORT=8080
"""

ACTIX_JWT_ENV = """\
PORT=8080
JWT_SECRET=change-me-in-production
"""

ACTIX_JWT_ENV_EXAMPLE = """\
PORT=8080
JWT_SECRET=your-secret-here
"""

ACTIX_SQLX_ENV = """\
PORT=8080
DATABASE_URL=sqlite::memory:
"""

ACTIX_SQLX_ENV_EXAMPLE = """\
PORT=8080
DATABASE_URL=sqlite:./data.db
"""
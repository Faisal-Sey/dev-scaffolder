# ── CARGO MANIFESTS ───────────────────────────────────────────────────────────

ROCKET_CARGO_TOML = """\
[package]
name = "{project_name}"
version = "0.1.0"
edition = "2021"

[dependencies]
rocket = { version = "0.5", features = ["json"] }
serde = { version = "1", features = ["derive"] }
serde_json = "1"
dotenv = "0.15"
"""

ROCKET_DIESEL_CARGO_TOML = """\
[package]
name = "{project_name}"
version = "0.1.0"
edition = "2021"

[dependencies]
rocket = { version = "0.5", features = ["json"] }
diesel = { version = "2.1", features = ["sqlite"] }
libsqlite3-sys = { version = "0.27", features = ["bundled"] }
serde = { version = "1", features = ["derive"] }
serde_json = "1"
dotenv = "0.15"
"""

# ── MAIN.RS FILES ─────────────────────────────────────────────────────────────

ROCKET_MAIN_RS = """\
#[macro_use]
extern crate rocket;

use rocket::serde::json::Json;
use serde_json::json;

#[get("/")]
fn index() -> Json<serde_json::Value> {
    Json(json!({ "message": "Hello from {project_name}!" }))
}

#[get("/health")]
fn health() -> Json<serde_json::Value> {
    Json(json!({ "status": "ok" }))
}

#[launch]
fn rocket() -> _ {
    dotenv::dotenv().ok();

    let port: u16 = std::env::var("PORT")
        .unwrap_or_else(|_| "8080".to_string())
        .parse()
        .expect("PORT must be a number");

    let config = rocket::Config {
        port,
        address: "0.0.0.0".parse().unwrap(),
        ..rocket::Config::default()
    };

    rocket::custom(config).mount("/", routes![index, health])
}
"""

ROCKET_REST_API_MAIN_RS = """\
#[macro_use]
extern crate rocket;

use rocket::http::Status;
use rocket::serde::json::Json;
use rocket::State;
use serde::{Deserialize, Serialize};
use serde_json::json;
use std::collections::HashMap;
use std::sync::Mutex;
use std::sync::atomic::{AtomicU64, Ordering};

#[derive(Debug, Clone, Serialize, Deserialize)]
struct Item {
    id: u64,
    title: String,
    description: Option<String>,
}

#[derive(Deserialize)]
struct ItemInput {
    title: String,
    description: Option<String>,
}

struct AppState {
    items: Mutex<HashMap<u64, Item>>,
    counter: AtomicU64,
}

#[get("/")]
fn index() -> Json<serde_json::Value> {
    Json(json!({ "message": "Hello from {project_name}!" }))
}

#[get("/health")]
fn health() -> Json<serde_json::Value> {
    Json(json!({ "status": "ok" }))
}

#[get("/api/items")]
fn list_items(state: &State<AppState>) -> Json<Vec<Item>> {
    Json(state.items.lock().unwrap().values().cloned().collect())
}

#[get("/api/items/<id>")]
fn get_item(state: &State<AppState>, id: u64) -> Option<Json<Item>> {
    state.items.lock().unwrap().get(&id).cloned().map(Json)
}

#[post("/api/items", data = "<body>")]
fn create_item(state: &State<AppState>, body: Json<ItemInput>) -> Json<Item> {
    let id = state.counter.fetch_add(1, Ordering::SeqCst);
    let item = Item { id, title: body.title.clone(), description: body.description.clone() };
    state.items.lock().unwrap().insert(id, item.clone());
    Json(item)
}

#[put("/api/items/<id>", data = "<body>")]
fn update_item(state: &State<AppState>, id: u64, body: Json<ItemInput>) -> Option<Json<Item>> {
    let mut items = state.items.lock().unwrap();
    if !items.contains_key(&id) {
        return None;
    }
    let item = Item { id, title: body.title.clone(), description: body.description.clone() };
    items.insert(id, item.clone());
    Some(Json(item))
}

#[delete("/api/items/<id>")]
fn delete_item(state: &State<AppState>, id: u64) -> Status {
    if state.items.lock().unwrap().remove(&id).is_some() {
        Status::NoContent
    } else {
        Status::NotFound
    }
}

#[launch]
fn rocket() -> _ {
    dotenv::dotenv().ok();

    let port: u16 = std::env::var("PORT")
        .unwrap_or_else(|_| "8080".to_string())
        .parse()
        .expect("PORT must be a number");

    let config = rocket::Config {
        port,
        address: "0.0.0.0".parse().unwrap(),
        ..rocket::Config::default()
    };

    rocket::custom(config)
        .manage(AppState {
            items: Mutex::new(HashMap::new()),
            counter: AtomicU64::new(1),
        })
        .mount("/", routes![index, health, list_items, get_item, create_item, update_item, delete_item])
}
"""

ROCKET_DIESEL_MAIN_RS = """\
#[macro_use]
extern crate rocket;

mod schema;

use diesel::prelude::*;
use diesel::sqlite::SqliteConnection;
use rocket::http::Status;
use rocket::serde::json::Json;
use rocket::State;
use serde::{Deserialize, Serialize};
use serde_json::json;
use std::sync::Mutex;

use schema::items;

#[derive(Debug, Clone, Serialize, Queryable)]
struct Item {
    id: i32,
    title: String,
    description: Option<String>,
}

#[derive(Insertable, Deserialize)]
#[diesel(table_name = items)]
struct NewItem {
    title: String,
    description: Option<String>,
}

type DbState = Mutex<SqliteConnection>;

#[get("/health")]
fn health() -> Json<serde_json::Value> {
    Json(json!({ "status": "ok" }))
}

#[get("/api/items")]
fn list_items(db: &State<DbState>) -> Json<Vec<Item>> {
    let conn = &mut *db.lock().unwrap();
    Json(items::table.load::<Item>(conn).unwrap_or_default())
}

#[get("/api/items/<item_id>")]
fn get_item(db: &State<DbState>, item_id: i32) -> Option<Json<Item>> {
    let conn = &mut *db.lock().unwrap();
    items::table.find(item_id).first::<Item>(conn).ok().map(Json)
}

#[post("/api/items", data = "<body>")]
fn create_item(db: &State<DbState>, body: Json<NewItem>) -> Json<Item> {
    let conn = &mut *db.lock().unwrap();
    diesel::insert_into(items::table)
        .values(&body.into_inner())
        .execute(conn)
        .expect("Failed to insert item");
    items::table.order(items::id.desc()).first::<Item>(conn).expect("Failed to fetch item").into()
}

#[put("/api/items/<item_id>", data = "<body>")]
fn update_item(db: &State<DbState>, item_id: i32, body: Json<NewItem>) -> Option<Json<Item>> {
    let conn = &mut *db.lock().unwrap();
    let n = diesel::update(items::table.find(item_id))
        .set((items::title.eq(&body.title), items::description.eq(&body.description)))
        .execute(conn)
        .unwrap_or(0);
    if n == 0 {
        return None;
    }
    items::table.find(item_id).first::<Item>(conn).ok().map(Json)
}

#[delete("/api/items/<item_id>")]
fn delete_item(db: &State<DbState>, item_id: i32) -> Status {
    let conn = &mut *db.lock().unwrap();
    match diesel::delete(items::table.find(item_id)).execute(conn) {
        Ok(n) if n > 0 => Status::NoContent,
        _ => Status::NotFound,
    }
}

fn setup_db(conn: &mut SqliteConnection) {
    diesel::sql_query(
        "CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT
        )",
    )
    .execute(conn)
    .expect("Failed to create items table");
}

#[launch]
fn rocket() -> _ {
    dotenv::dotenv().ok();

    let port: u16 = std::env::var("PORT")
        .unwrap_or_else(|_| "8080".to_string())
        .parse()
        .expect("PORT must be a number");

    let database_url = std::env::var("DATABASE_URL")
        .unwrap_or_else(|_| ":memory:".to_string());

    let mut conn = SqliteConnection::establish(&database_url)
        .expect("Failed to connect to database");
    setup_db(&mut conn);

    let config = rocket::Config {
        port,
        address: "0.0.0.0".parse().unwrap(),
        ..rocket::Config::default()
    };

    rocket::custom(config)
        .manage(Mutex::new(conn))
        .mount("/", routes![health, list_items, get_item, create_item, update_item, delete_item])
}
"""

ROCKET_DIESEL_SCHEMA_RS = """\
diesel::table! {
    items (id) {
        id -> Integer,
        title -> Text,
        description -> Nullable<Text>,
    }
}
"""

ROCKET_TESTING_MAIN_RS = """\
#[macro_use]
extern crate rocket;

use rocket::serde::json::Json;
use serde_json::json;

#[get("/")]
fn index() -> Json<serde_json::Value> {
    Json(json!({ "message": "Hello from {project_name}!" }))
}

#[get("/health")]
fn health() -> Json<serde_json::Value> {
    Json(json!({ "status": "ok" }))
}

pub fn build_rocket() -> rocket::Rocket<rocket::Build> {
    dotenv::dotenv().ok();

    let port: u16 = std::env::var("PORT")
        .unwrap_or_else(|_| "8080".to_string())
        .parse()
        .expect("PORT must be a number");

    let config = rocket::Config {
        port,
        address: "0.0.0.0".parse().unwrap(),
        ..rocket::Config::default()
    };

    rocket::custom(config).mount("/", routes![index, health])
}

#[launch]
fn rocket() -> _ {
    build_rocket()
}

#[cfg(test)]
mod tests {
    use super::*;
    use rocket::http::Status;
    use rocket::local::blocking::Client;

    #[test]
    fn test_health_returns_ok() {
        let client = Client::tracked(build_rocket()).expect("valid rocket instance");
        let response = client.get("/health").dispatch();
        assert_eq!(response.status(), Status::Ok);
    }

    #[test]
    fn test_index_returns_message() {
        let client = Client::tracked(build_rocket()).expect("valid rocket instance");
        let response = client.get("/").dispatch();
        assert_eq!(response.status(), Status::Ok);
        let body: serde_json::Value = response.into_json().unwrap();
        assert!(body["message"].is_string());
    }
}
"""

# ── DOCKER ────────────────────────────────────────────────────────────────────

ROCKET_DOCKERFILE = """\
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

ROCKET_DIESEL_DOCKERFILE = """\
FROM rust:1.76 AS builder
RUN apt-get update && apt-get install -y libsqlite3-dev && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY Cargo.toml ./
RUN mkdir src && echo 'fn main() {}' > src/main.rs && \
    cargo build --release && \
    rm -rf src
COPY src ./src
RUN cargo build --release

FROM debian:bookworm-slim AS runtime
RUN apt-get update && apt-get install -y libsqlite3-0 ca-certificates && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY --from=builder /app/target/release/{project_name} ./server
EXPOSE 8080
ENV PORT=8080
CMD ["./server"]
"""

ROCKET_DOCKER_COMPOSE_YML = """\
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

ROCKET_DOCKERIGNORE = """\
target/
.git/
.env
*.md
"""

# ── MISC ──────────────────────────────────────────────────────────────────────

ROCKET_TOML = """\
[default]
port = 8080
address = "0.0.0.0"
log_level = "normal"
"""

ROCKET_GITIGNORE = """\
/target
.env
"""

ROCKET_ENV = """\
PORT=8080
"""

ROCKET_ENV_EXAMPLE = """\
PORT=8080
"""

ROCKET_DIESEL_ENV = """\
PORT=8080
DATABASE_URL=:memory:
"""

ROCKET_DIESEL_ENV_EXAMPLE = """\
PORT=8080
DATABASE_URL=./data.db
"""
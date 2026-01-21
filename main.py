from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from database import create_tables
from routers import meetings_router, notes_router, tasks_router, users_router

app = FastAPI(
    title="Meeting Notes API",
    description="API for managing meetings, notes, and tasks",
    version="1.0.0"
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    create_tables()
    yield
    # shutdown


app.include_router(users_router)
app.include_router(meetings_router)
app.include_router(notes_router)
app.include_router(tasks_router)


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def root():
    """
    Static landing page for API navigation.
    """
    return """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Meeting Notes API • solo.one</title>
    <style>
      :root {
        color-scheme: light;
        --bg: #f7f8fb;
        --card: #ffffff;
        --text: #0f172a;
        --muted: #64748b;
        --accent: #2563eb;
        --accent-soft: rgba(37, 99, 235, 0.12);
        --border: #e2e8f0;
      }
      * { box-sizing: border-box; }
      body {
        margin: 0;
        font-family: "Inter", "Segoe UI", system-ui, -apple-system, sans-serif;
        background: var(--bg);
        color: var(--text);
      }
      .container {
        min-height: 100vh;
        display: grid;
        place-items: center;
        padding: 48px 24px;
      }
      .card {
        width: min(900px, 100%);
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 20px;
        padding: 36px;
        box-shadow: 0 18px 45px rgba(15, 23, 42, 0.08);
      }
      .badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        font-size: 13px;
        font-weight: 600;
        letter-spacing: 0.4px;
        text-transform: uppercase;
        color: var(--accent);
        background: var(--accent-soft);
        padding: 6px 12px;
        border-radius: 999px;
      }
      h1 {
        margin: 18px 0 8px;
        font-size: clamp(28px, 3vw, 40px);
      }
      p {
        margin: 0 0 16px;
        color: var(--muted);
        line-height: 1.6;
      }
      .links {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        margin-top: 22px;
      }
      a.button {
        text-decoration: none;
        color: #fff;
        background: var(--accent);
        padding: 10px 18px;
        border-radius: 10px;
        font-weight: 600;
        font-size: 14px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        box-shadow: 0 10px 20px rgba(37, 99, 235, 0.2);
      }
      a.button.secondary {
        color: var(--accent);
        background: transparent;
        border: 1px solid var(--accent);
        box-shadow: none;
      }
      a.button:hover {
        transform: translateY(-1px);
      }
      .meta {
        margin-top: 26px;
        font-size: 13px;
        color: var(--muted);
        display: flex;
        flex-wrap: wrap;
        gap: 16px;
      }
      .meta span {
        background: #f1f5f9;
        padding: 6px 12px;
        border-radius: 999px;
        border: 1px solid var(--border);
      }
    </style>
  </head>
  <body>
    <div class="container">
      <section class="card">
        <span class="badge">solo.one • technical challenge</span>
        <h1>Meeting Notes API</h1>
        <p>
          A clean FastAPI service for meetings, notes, and tasks.
          Use the links below to explore the documentation and schema.
        </p>
        <div class="links">
          <a class="button" href="/docs">Open Swagger UI</a>
          <a class="button secondary" href="/redoc">Open ReDoc</a>
          <a class="button secondary" href="/openapi.json">Download OpenAPI</a>
        </div>
        <div class="meta">
          <span>Author: Wilson Moraes dos Santos</span>
          <span>Company: solo.one</span>
          <span>Version: 1.0.0</span>
        </div>
      </section>
    </div>
  </body>
</html>"""


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

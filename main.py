from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI

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


@app.get("/")
async def root():
    """
    Root endpoint to verify the API is running.
    """
    return {
        "message": "Welcome to the Meeting Notes API",
        "version": "1.0.0",
        "endpoints": {
            "users": "/users/",
            "meetings": "/meetings/",
            "notes": "/notes/",
            "tasks": "/tasks/"
        }
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

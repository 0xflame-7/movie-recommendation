from fastapi import FastAPI, status
from contextlib import asynccontextmanager
from src.db import init_db
from src.api.routes import auth_router, user_router
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def life_span(app: FastAPI):
    print("Application is starting...")
    await init_db()
    yield
    print("Application is shutting down...")


app = FastAPI(title="FilmFlare", description="FilmFlare API", lifespan=life_span)

app.include_router(auth_router)
app.include_router(user_router)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Development origin
        # "https://your-production-domain.com"  # Production origin
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
)


@app.get("/", status_code=status.HTTP_200_OK)
async def health() -> dict[str, str]:
    return {"status": "ok", "message": "Hello from server!"}

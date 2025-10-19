from fastapi import FastAPI, status
from contextlib import asynccontextmanager
from src.db import init_db
from src.api.routes import router as auth_router


@asynccontextmanager
async def life_span(app: FastAPI):
    print("Application is starting...")
    await init_db()
    yield
    print("Application is shutting down...")


app = FastAPI(title="FilmFlare", description="FilmFlare API", lifespan=life_span)

app.include_router(auth_router)


@app.get("/", status_code=status.HTTP_200_OK)
async def health() -> dict[str, str]:
    return {"status": "ok", "message": "Hello from server!"}

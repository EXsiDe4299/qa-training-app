from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from qa_training_app.api.router import router as api_router
from qa_training_app.config import settings
from qa_training_app.db import init_db
from qa_training_app.frontend.router import router as frontend_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="QA Training App",
    description=(
        "Simple request tracker for QA practice: register, login, "
        "create and delete requests."
    ),
    lifespan=lifespan,
)

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.session_secret,
    max_age=60 * 60 * 24 * 7,
)

app.mount(
    "/static",
    StaticFiles(directory=settings.base_dir / "static"),
    name="static",
)

app.include_router(api_router)
app.include_router(frontend_router, include_in_schema=False)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

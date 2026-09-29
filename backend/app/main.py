from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes.analytics import router as analytics_router
from app.api.routes.employees import router as employees_router
from app.db.models import Base
from app.db.session import engine


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Salary Management API", lifespan=lifespan)
app.include_router(employees_router, prefix="/api")
app.include_router(analytics_router, prefix="/api")

FRONTEND_DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"
FRONTEND_INDEX = FRONTEND_DIST / "index.html"
if FRONTEND_INDEX.is_file():
    ASSETS_DIRECTORY = FRONTEND_DIST / "assets"
    if ASSETS_DIRECTORY.is_dir():
        app.mount(
            "/assets",
            StaticFiles(directory=ASSETS_DIRECTORY),
            name="frontend-assets",
        )

    @app.get("/{requested_path:path}", include_in_schema=False)
    def serve_frontend(requested_path: str) -> FileResponse:
        if requested_path == "api" or requested_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="Not found")

        requested_file = (FRONTEND_DIST / requested_path).resolve()
        if requested_file.is_relative_to(FRONTEND_DIST.resolve()) and requested_file.is_file():
            return FileResponse(requested_file)
        return FileResponse(FRONTEND_INDEX)
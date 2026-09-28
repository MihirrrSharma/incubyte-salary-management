from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes.employees import router as employees_router
from app.db.models import Base
from app.db.session import engine


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Salary Management API", lifespan=lifespan)
app.include_router(employees_router, prefix="/api")
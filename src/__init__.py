from fastapi import FastAPI
from src.books.routes import book_router
from contextlib import asynccontextmanager
from src.db.main import init_db

@asynccontextmanager
async def Life_span(app: FastAPI):
    print("server started...")
    await init_db()
    yield
    print("server stopped...")

version = "v1"

app = FastAPI(
    title="Booly",
    description="A REST API for a book review web service",
    version=version,
    lifespan=Life_span

)


app.include_router(book_router, prefix=f"/api/{version}/books",tags=["books"])
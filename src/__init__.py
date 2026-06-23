from fastapi import FastAPI
from src.books.routes import book_router
from src.reviews.routers import review_router
from src.auth.routes import auth_router
from src.tags.routes import tags_router
from src.errors import (
    register_error_handlers,
)

from src.middleware import register_middleware




version = "v1"

description = """
A REST API for a book review web service.

This REST API is able to;
- Create Read Update And delete books
- Add reviews to books
- Add tags to Books e.t.c.
    """

version_prefix ="/api/{version}"

app = FastAPI(
    title="Booly",
    description=description,
    version=version,
    license_info={"name": "MIT License", "url": "https://opensource.org/license/mit"},
    contact={
        "name": "Playmaker",
        "url": "https://github.com/DwainYu",
        "email": "Playmaker@qq.com",
    },
    
    openapi_url=f"{version_prefix}/openapi.json",
    docs_url=f"{version_prefix}/docs",
    redoc_url=f"{version_prefix}/redoc"
    


)

register_middleware(app)

register_error_handlers(app)  

app.include_router(book_router, prefix=f"/api/{version}/books",tags=["books"])
app.include_router(auth_router, prefix=f"/api/{version}/auth",tags=["auth"])
app.include_router(review_router, prefix=f"/api/{version}/reviews",tags=["reviews"])
app.include_router(tags_router, prefix=f"/api/{version}/tags",tags=["tags"])

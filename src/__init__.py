from fastapi import FastAPI
from src.books.routes import book_router
from src.reviews.routers import review_router
from src.auth.routes import auth_router
from src.tags.routes import tags_router
from src.errors import (
    register_error_handlers,
)

from contextlib import asynccontextmanager
from src.db.main import init_db




# 应用生命周期管理器作用：在FastAPI应用启动和停止时执行一些操作比如：初始化数据库、关闭数据库连接等
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

    #lifespan=Life_span,注释生命周期管理器，应用启动时不会执行init_db函数，初始化数据库


)


register_error_handlers(app)  

app.include_router(book_router, prefix=f"/api/{version}/books",tags=["books"])
app.include_router(auth_router, prefix=f"/api/{version}/auth",tags=["auth"])
app.include_router(review_router, prefix=f"/api/{version}/reviews",tags=["reviews"])
app.include_router(tags_router, prefix=f"/api/{version}/tags",tags=["tags"])

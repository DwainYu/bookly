from sqlmodel import create_engine
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncEngine
from src.config import Config

from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker
from collections.abc import AsyncGenerator

# 异步数据库引擎
async_engine = AsyncEngine(
    create_engine(
        url=Config.DATABASE_URL, 
       
        )
)

# 初始化数据库
async def init_db() -> None:
    """create a connection to our db"""

    async with async_engine.begin() as conn:
        

        await conn.run_sync(SQLModel.metadata.create_all)

# 获取异步数据库会话
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """get a async session from the db"""
    Session = sessionmaker(
        # 绑定异步引擎
        bind=async_engine,
        # 使用异步会话
        class_=AsyncSession,
        # 禁用会话过期
        # 这样可以确保在会话中进行的查询操作
        # 不会被自动提交到数据库
        expire_on_commit=False
        )
    
    # 创建异步会话以便我们能在路由中使用它
    async with Session() as session:
        #yield session的作用：将会话对象返回给路由函数，以便在路由中使用它
        yield session

    # async with AsyncSession(async_engine) as session:
    #     yield session
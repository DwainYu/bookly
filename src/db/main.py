from sqlmodel import create_engine
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncEngine
from src.config import Config
from src.books.models import Book

engine = AsyncEngine(
    create_engine(
        url=Config.DATABASE_URL, 
        echo=True
        )
)


async def init_db():
    """create a connection to our db"""

    async with engine.begin() as conn:
        

        await conn.run_sync(SQLModel.metadata.create_all)

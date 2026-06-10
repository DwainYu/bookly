# 书服务层
from .schemas import BookUpdateModel

# 引入异步会话
from sqlalchemy.ext.asyncio import AsyncSession

# 引入书籍创建模型
from .schemas import BookCreateModel

from sqlmodel import select, desc
from src.db.models import Book

import uuid


class BookService:
    async def get_all_books(self, session: AsyncSession):
        """get all books"""
        statement = select(Book).order_by(desc(Book.created_at))
        result = await session.exec(statement)
        books = result.all()
        # session.exec(statement) 是异步方法，返回的是一个协程对象，但你在它上面直接调用了 .all()方法，所以需要等待协程对象执行完成。协程对象是一个待执行的异步任务。
        return books

    async def get_book(self, book_uid: str, session: AsyncSession):
        """get book by uid"""
        statement = select(Book).where(Book.uid == uuid.UUID(book_uid))
        result = await session.exec(statement)

        book = result.first()

        return book if book is not None else None

    async def get_user_books(self, user_id: str, session: AsyncSession):
        """get user books"""
        statement = (
            select(Book)
            .where(Book.user_id == uuid.UUID(user_id))
            .order_by(desc(Book.created_at))
        )
        result = await session.exec(statement)
        books = result.all()
        # session.exec(statement) 是异步方法，返回的是一个协程对象，但你在它上面直接调用了 .all()方法，所以需要等待协程对象执行完成。协程对象是一个待执行的异步任务。
        return books

    async def create_book(
        self, book_data: BookCreateModel, session: AsyncSession, user_id: str
    ):
        """create a new book"""
        # 将BookCreateModel转换为字典，model_dump()方法返回的是字典。
        # **book_data_dict是将字典展开为关键字参数。
        # 例如，**book_data_dict可以将字典转换为关键字参数，例如：Book(**book_data_dict)。
        book_data_dict = book_data.model_dump()
        new_book = Book(**book_data_dict)
        # 一定要用uuid.UUID(user_id)转换为uuid类型，否则会报错
        new_book.user_id = uuid.UUID(user_id)
        session.add(new_book)
        await session.commit()
        await session.refresh(new_book)
        return new_book

    async def update_book(
        self, book_uid: str, book_data: BookUpdateModel, session: AsyncSession
    ):
        """update a book"""
        book_to_update = await self.get_book(book_uid, session)
        if book_to_update is not None:
            book_data_dict = (
                book_data.model_dump()
            )  # 将BookUpdateModel转换为字典，model_dump()方法返回的是字典。

            for key, value in book_data_dict.items():
                setattr(book_to_update, key, value)
                # 为什么用setattr？因为setattr()可以动态地设置对象的属性值。
                # 例如，setattr(book_to_update, "title", "Think Python")可以将book_to_update的title属性设置为"Think Python"。

            await session.commit()
            return book_to_update
        else:
            return None  # 如果没有找到，返回None。

    async def delete_book(self, book_uid: str, session: AsyncSession):
        """delete a book"""
        book_to_delete = await self.get_book(book_uid, session)
        if book_to_delete is not None:
            await session.delete(book_to_delete)
            await session.commit()
            return book_to_delete
        else:
            return None

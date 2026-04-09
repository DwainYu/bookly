from .schemas import BookUpdateModel
from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import BookCreateModel, BookUpdateModel
from sqlmodel import select,desc
from .models import Book

class BookService:
    async def get_all_books(self, session: AsyncSession):
        # 为什么使用session，而不是直接使用db？因为session是异步的，而db是同步的。异步的session可以更高效地处理异步操作，而同步的db只能处理同步操作。
        """get all books"""
        statement = select(Book).order_by(desc(Book.created_at))#降序排列
        result = await session.exec(statement).all() # 为什么使用await？因为session.exec是一个异步操作，需要等待它完成才能获取结果。
        return result.all()

    async def get_book(self, book_uid: str, session: AsyncSession):
        """get book by uid"""
        statement = select(Book).where(Book.uid == book_uid)
        result = await session.exec(statement).first() #exec是执行sql语句，first是获取第一条记录
        book = result.first()
        
        return book or None# 如果没有找到，返回None。



    async def create_book(self, book_data: BookCreateModel, session: AsyncSession):
        """create a new book"""
        book_data_dict = book_data.model_dump()
        new_book = Book(**book_data_dict) 
        # 为什么用**book_data_dict？因为model_dump()返回的是字典，而Book的参数是关键字参数。
        # **book_data_dict是将字典展开为关键字参数。
        await session.add(new_book)
        await session.commit()
        return new_book

    async def update_book(
        self, book_uid: str, book_data: BookUpdateModel, session: AsyncSession
    ):
        """update a book"""
        book_to_update = await self.get_book(book_uid, session)
        if  book_to_update:
            book_data_dict = book_data.model_dump()

            for key, value in book_data_dict.items():
                setattr(book_to_update, key, value)
                # 为什么用setattr？因为setattr()可以动态地设置对象的属性值。
                # 例如，setattr(book_to_update, "title", "Think Python")可以将book_to_update的title属性设置为"Think Python"。

            await session.commit()
            return book_to_update
        else:
            return None # 如果没有找到，返回None。



    async def delete_book(self, book_uid: str, session: AsyncSession):
        """delete a book"""
        book_to_delete = await self.get_book(book_uid, session)
        if book_to_delete:
            await session.delete(book_to_delete)
            await session.commit()
            return book_to_delete
        else:
            return None
       

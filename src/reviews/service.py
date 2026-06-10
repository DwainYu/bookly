

import uuid

from src.errors import BookNotFound, UserNotFound
from src.errors import InsufficientPermission
from fastapi import HTTPException
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.models import Review
from src.auth.service import UserService
from src.books.service import BookService
from src.reviews.schemas import ReviewCreateModel


book_service = BookService()
user_service = UserService()


class ReviewService:
    async def add_review_to_book(
        self,
        user_email: str,
        book_uid: str,
        review_data: ReviewCreateModel,
        session: AsyncSession,
    ):
        try:
            book = await book_service.get_book(
                book_uid=book_uid,
                session=session,
            )
            user = await user_service.get_user_by_email(
                email=user_email,
                session=session,
            )

            review_data_dict = review_data.model_dump()
            # **号表示将review_data中的属性值,赋值给new_review的属性
            new_review = Review(**review_data_dict)
            if book is None:
                raise BookNotFound()
            if user is None:
                raise UserNotFound()

            # 将user和book赋值给new_review的user和book属性,与赋值uid的区别是,赋值uid时,需要先查询user和book,再赋值给new_review的user和book属性
            # 而赋值user和book时,直接赋值即可,无需查询
            new_review.user = user
            new_review.book = book

            session.add(new_review)
            await session.commit()
            return new_review

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=str(e),
            )
        

    async def get_review(self, review_uid: str, session: AsyncSession):
        # 使用 session.get() 替代 select+exec+first() 的原因：
        # 1. session.get() 返回完整的 SQLModel 实例，包含所有字段和 relationships
        # 2. select+exec+first() 返回 Row 对象，relationship 字段无法被正确序列化
        # 3. Review 模型有 user 和 book 两个 Relationship 字段，Row 对象无法正确处理
        # 4. session.get() 通过主键直接查询，更高效
        review = await session.get(Review, uuid.UUID(review_uid))
        return review

    async def get_all_reviews(self, session: AsyncSession):
        statement = select(Review).order_by(desc(Review.created_at))

        result = await session.exec(statement)

        return result.all()

    async def delete_review_to_from_book(
        self, review_uid: str, user_email: str, session: AsyncSession
    ):
        user = await user_service.get_user_by_email(user_email, session)

        review = await self.get_review(review_uid, session)

        if not review or (review.user != user):
            raise InsufficientPermission()

        session.delete(review)

        await session.commit()

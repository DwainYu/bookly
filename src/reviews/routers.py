
from fastapi import APIRouter, Depends
from src.db.models import User
from src.reviews.schemas import ReviewCreateModel, ReviewModel
from src.reviews.service import ReviewService

from src.auth.dependencies import get_current_user, RoleChecker
from src.db.main import get_session
from sqlalchemy.ext.asyncio import AsyncSession



review_service = ReviewService()
review_router = APIRouter()
admin_role_checker = Depends(RoleChecker(["admin"]))
user_role_checker = Depends(RoleChecker(["user", "admin"]))


@review_router.get("/", dependencies=[admin_role_checker,])
async def get_all_reviews(
    session: AsyncSession = Depends(get_session),
):
    reviews = await review_service.get_all_reviews(session)
    return reviews

@review_router.post("/book/{book_uid}", dependencies=[user_role_checker])
async def add_review_to_book(
    book_uid: str,
    review_data: ReviewCreateModel,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    new_review = await review_service.add_review_to_book(
        user_email=current_user.email,
        
        review_data=review_data,
        book_uid=book_uid,
        session=session,
    )
    return new_review

@review_router.get("/{review_uid}", response_model=ReviewModel, dependencies=[user_role_checker])
async def get_review(
    review_uid: str,
    session: AsyncSession = Depends(get_session),
):
    # 添加 response_model=ReviewModel 的原因：
    # 1. FastAPI 会根据 response_model 自动调用 Pydantic 模型验证响应数据
    # 2. 与 Book 路由的处理方式保持一致
    # 3. 确保 SQLModel 对象（包括 relationships）被正确序列化为 JSON
    review = await review_service.get_review(review_uid, session)
    
    return review
    
@review_router.delete("/{review_uid}",  dependencies=[user_role_checker])
async def delete_review(
    review_uid: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    review = await review_service.get_review(review_uid, session)
    if review:
        await review_service.delete_review_to_from_book(review_uid, current_user.email, session=session)
        return {"message": "Review deleted successfully"}


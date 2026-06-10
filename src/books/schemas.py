from src.reviews.schemas import ReviewModel
from pydantic import Field
from pydantic import BaseModel
import uuid
from datetime import datetime, date

class Book(BaseModel):
    uid: uuid.UUID
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str
    created_at: datetime
    update_at: datetime

#创建一个类用于输出图书的所有评论
class BookDetailModel(Book):
    reviews: list[ReviewModel] = Field(description="List of reviews for the book")

class BookCreateModel(BaseModel):
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str

class BookUpdateModel(BaseModel):

    title: str
    author: str
    publisher: str
    page_count: int
    language: str

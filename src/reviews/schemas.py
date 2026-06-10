from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
import uuid

class ReviewModel(BaseModel):
    uid: uuid.UUID = Field(description="Unique identifier of the review")
    rating: int = Field(lt=5,description="Rating of the review")
    review_text: str = Field(description="Text of the review")
    user_uid: Optional[uuid.UUID] = Field(description="User ID of the review")
    book_uid: Optional[uuid.UUID] = Field(description="Book UID of the review")
    created_at: datetime = Field(description="Timestamp of the review")
    update_at: datetime = Field(description="Timestamp of the review update")

# 创建评论模型为什么继承BaseModel,而不是ReviewModel
# 因为ReviewModel已经包含了uid,而创建评论时,不需要uid,只需要rating和review_text
class ReviewCreateModel(BaseModel):
    rating: int = Field(lt=5,description="Rating of the review")
    review_text: str = Field(description="Text of the review")
    



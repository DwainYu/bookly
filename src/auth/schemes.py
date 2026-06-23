#导入pydantic模块
from pydantic import BaseModel, Field
from datetime import datetime
import uuid
from typing import List
from src.books.schemas import Book, ReviewModel



class UserCreateModel(BaseModel):


    # 用户名
    first_name: str = Field(max_length=20, description="姓名")
    last_name: str = Field(max_length=20, description="姓氏")
    # 用户名
    username: str = Field(max_length=8, description="用户名")
    # 邮箱
    email: str = Field(max_length=50, description="邮箱")
    # 密码
    password: str = Field(min_length=8, description="密码")

class UserModel(BaseModel):
    uid: uuid.UUID 
    username: str
    email: str
    first_name: str
    last_name: str
    is_verified: bool = False
    # 密码哈希值，exclude=True表示在序列化时排除该字段，防止泄露密码
    password_hash: str = Field(exclude=True)

    # 创建时间和更新时间
    created_at: datetime 
    update_at: datetime 
    # 关联书籍表的目的：
    # 1. 可以获取用户的书籍书籍信息。
    # 2. 可以根据用户的书籍书籍信息进行权限检查。


class UserBooksModel(UserModel):
    books: List[Book]
    reviews: List[ReviewModel]

class UserLoginModel(BaseModel):
    email: str = Field(max_length=50, min_length=4, description="邮箱")
    password: str = Field(min_length=8, description="密码")

class EmailModel(BaseModel):
    address: list[str]


class PasswordResetRequestModel(BaseModel):
    email: str


class PasswordResetConfirmModel(BaseModel):
    new_password: str
    confirm_new_password: str
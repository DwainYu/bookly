from sqlmodel import SQLModel, Field, Column, Relationship
import uuid
from datetime import datetime, date
import sqlalchemy.dialects.postgresql as pg
from typing import List
from typing import Optional


# 用户模型
class User(SQLModel, table=True):
    __tablename__ = "users"

    uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            nullable=False,
            primary_key=True,
            default=uuid.uuid4,  # 为什么用uuid4？因为uuid4是随机生成一个UUID。
        )
    )
    username: str
    email: str
    first_name: str
    last_name: str
    role: str = Field(sa_column=Column(pg.VARCHAR(50), nullable=False, default="user"))
    is_verified: bool = Field(default=False)
    # 密码哈希值，exclude=True表示在序列化时排除该字段，防止泄露密码
    password_hash: str = Field(exclude=True)

    # 创建时间和更新时间
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    update_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    # 关联书籍表的目的：
    # 1. 可以获取用户的书籍书籍信息。
    # 2. 可以根据用户的书籍信息进行权限检查。
    # 加载方式：
    # 1. 当查询用户时，会自动加载该用户的书籍书籍信息。
    # 2. 可以根据用户的书籍书籍信息进行权限检查。
    books: List["Book"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"lazy": "selectin"}
    )
    # 关联评论表的目的：
    # 1. 可以获取用户的评论信息。
    # 2. 可以根据用户的评论信息进行权限检查。
    # 加载方式：
    # 1. 当查询用户时，会自动加载该用户的评论信息。
    # 2. 可以根据用户的评论信息进行权限检查。
    reviews: List["Review"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"lazy": "selectin"}
    )

    # __repr__方法的作用1：当打印对象时，返回一个字符串，方便调试。2：当对象作为字典类型。
    def __repr__(self) -> str:
        return f"<User {self.username}>"






# 书籍标签关联表
class BookTag(SQLModel, table=True):
    book_id: uuid.UUID = Field(default=None, foreign_key="books.uid", primary_key=True)
    tag_id: uuid.UUID = Field(default=None, foreign_key="tags.uid", primary_key=True)

# 标签表
class Tag(SQLModel, table=True):
    __tablename__ = "tags"
    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    name: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    books: List["Book"] = Relationship(
        link_model=BookTag,
        back_populates="tags",
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    def __repr__(self) -> str:
        return f"<Tag {self.name}>"

class Book(SQLModel, table=True):
    __tablename__ = "books"

    uid: uuid.UUID = Field(
        sa_column=Column(  # 为什么用sa_column？因为SQLModel的Column和SQLAlchemy的Column是不同的
            pg.UUID,
            nullable=False,
            primary_key=True,
            default=uuid.uuid4,  # 为什么用uuid4？因为uuid4是随机生成一个UUID。
        )
    )
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str
    user_uid: Optional[uuid.UUID] = Field(
        default=None, foreign_key="users.uid", nullable=True
    )
    # 为什么用Optional？因为user_uid是可选的，所以用Optional[uuid.UUID]表示user_uid可以为空。
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    update_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    # 关联用户表的目的：
    # 1. 可以获取书籍的创建者信息。
    # 2. 可以根据书籍的创建者信息进行权限检查。
    # 为什么用Optional？因为user是可选的，所以用Optional[User]表示user可以为空。
    user: Optional[User] = Relationship(back_populates="books")
    # 关联评论表的目的：
    # 1. 可以获取书籍的评论信息。
    # 2. 可以根据书籍的评论信息进行权限检查。
    # 加载方式：
    # 1. 当查询书籍时，会自动加载该书籍的评论信息。
    # 2. 可以根据书籍的评论信息进行权限检查。
    reviews: List["Review"] = Relationship(
        back_populates="book", sa_relationship_kwargs={"lazy": "selectin"}
    )
    # 关联标签表的目的：
    # 1. 可以获取书籍的标签信息。
    # 2. 可以通过标签筛选书籍。
    # 加载方式：
    # 1. 当查询书籍时，会自动加载该书籍的标签信息。
    tags: List[Tag] = Relationship(
        link_model=BookTag,
        back_populates="books",
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    # 重写__repr__方法，返回Book对象的标题
    def __repr__(self) -> str:
        return f"<Book {self.title}>"

class Review(SQLModel, table=True):
    __tablename__ = "reviews"
    uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            nullable=False,
            primary_key=True,
            default=uuid.uuid4,  # 为什么用uuid4？因为uuid4是随机生成一个UUID。
        )
    )

    rating: int = Field(lt=5)
    review_text: str = Field(sa_column=Column(pg.VARCHAR(255), nullable=False))
    user_uid: Optional[uuid.UUID] = Field(
        default=None, foreign_key="users.uid", nullable=True
    )
    book_uid: Optional[uuid.UUID] = Field(
        default=None, foreign_key="books.uid", nullable=True
    )

    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    update_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    # 关联用户表的目的：
    # 1. 可以获取评论的创建者信息。
    # 2. 可以根据评论的创建者信息进行权限检查。
    # 为什么用Optional？因为user是可选的，所以用Optional[User]表示user可以为空。
    user: Optional[User] = Relationship(back_populates="reviews")
    book: Optional[Book] = Relationship(back_populates="reviews")

    # 重写__repr__方法，返回Review对象的详细信息
    def __repr__(self) -> str:
        return f"<Review for book {self.book_uid} by user {self.user_uid}>"

    ... # the rest of the file
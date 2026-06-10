# 引入书籍模型
from src.books.schemas import Book, BookCreateModel, BookUpdateModel, BookDetailModel   

# 引入依赖注入
from fastapi import APIRouter, status, Depends



# 引入数据库会话
from src.db.main import get_session

# 引入异步会话
from sqlmodel.ext.asyncio.session import AsyncSession

# 引入书籍服务
from src.books.service import BookService

# 引入访问令牌依赖项
from src.auth.dependencies import AccessTokenBearer

# 引入角色检查依赖项
from src.auth.dependencies import RoleChecker

# 引入书籍不存在异常
from src.errors import BookNotFound



# 路由器
book_router = APIRouter()
# 书籍服务
book_service = BookService()
# 引入访问令牌依赖项
access_token_bearer = AccessTokenBearer()
# 引入角色检查依赖项
role_checker = RoleChecker(["admin", "user"])

#依赖项是什么? session: AsyncSession = Depends(get_session)
# 从依赖项中获取数据库会话对象
# 从依赖项中获取用户信息
#注入依赖是什么? 从依赖项中获取数据库会话对象和用户信息。
#为什么叫注入? 因为依赖项是注入到函数中，而不是在函数中创建依赖项。

# 获取所有书籍，response_model=list[Book] 表示返回一个书籍列表
@book_router.get("/", response_model=list[Book], dependencies=[Depends(role_checker)])
async def get_all_books(
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
    
):

    """获取 all books"""
    # 为什么book_service前需要await？
    # 因为book_service是一个异步函数，需要等待它执行完成才能返回结果
    books = await book_service.get_all_books(session)
    return books

@book_router.get("/user/{user_id}", response_model=list[Book], dependencies=[Depends(role_checker)])
async def get_user_books(
    user_id: str,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
    
):

    """获取 all books"""
    # 为什么book_service前需要await？
    # 因为book_service是一个异步函数，需要等待它执行完成才能返回结果
    books = await book_service.get_user_books(user_id, session)
    return books


# 为create_a_books函数添加response_model注解，保持API响应类型一致性
@book_router.post("/", status_code=status.HTTP_201_CREATED, response_model=Book, dependencies=[Depends(role_checker)])
async def create_a_books(
    book_data: BookCreateModel,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
) -> dict:
    """创建 a book"""
    user_id = token_details['user_data']['user_uid']
    new_book = await book_service.create_book(book_data, session,user_id=user_id)
    return new_book


# 为get_book函数添加response_model注解，保持API响应类型一致性
@book_router.get("/{book_uid}", response_model=BookDetailModel, dependencies=[Depends(role_checker)])
async def get_book(
    book_uid: str,
    session: AsyncSession = Depends(get_session),
    token_details: str = Depends(access_token_bearer),
) -> dict:
    book = await book_service.get_book(book_uid, session)
    if book:
        return book
    else:
        raise BookNotFound()


# 为update_book函数添加response_model注解，保持API响应类型一致性
@book_router.patch("/{book_uid}", response_model=Book, dependencies=[Depends(role_checker)])
async def update_book(
    book_uid: str,
    book_update: BookUpdateModel,
    session: AsyncSession = Depends(get_session),
    token_details: str = Depends(access_token_bearer),
) -> dict:
    """更新 a book"""
    updated_book = await book_service.update_book(book_uid, book_update, session)
    if updated_book:
        return updated_book
    else:
        raise BookNotFound()


# 为delete_book函数添加response_model注解，保持API响应类型一致性
@book_router.delete("/{book_uid}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(role_checker)])
async def delete_book(
    book_uid: str,
    session: AsyncSession = Depends(get_session),
    token_details: str = Depends(access_token_bearer),
):
    """删除 a book"""
    book_to_delete = await book_service.delete_book(book_uid, session)
    if not book_to_delete:
        raise BookNotFound()


from typing import Any, Callable
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi import FastAPI, status


class BooklyException(Exception):
    """
    自定义异常类，用于处理Bookly应用中的异常情况。
    """

    pass


class InvalidToken(BooklyException):
    """
    无效的令牌异常类。
    """

    pass


class RevokedToken(BooklyException):
    """
    已撤销的令牌异常类。
    """

    pass


class AccessTokenRequired(BooklyException):
    """
    访问令牌必填异常类。
    """

    pass


class RefreshTokenRequired(BooklyException):
    """
    刷新令牌必填异常类。
    """

    pass


class UserAlreadyExists(BooklyException):
    """
    用户已存在异常类。
    """

    pass


class InvalidCredentials(BooklyException):
    """
    无效的凭据异常类。,填错用户名或密码,邮箱不存在
    """

    pass


class InsufficientPermission(BooklyException):
    """
    权限不足异常类。
    """

    pass


class BookNotFound(BooklyException):
    """
    书籍不存在异常类。
    """

    pass


class TagNotFound(BooklyException):
    """
    标签不存在异常类。
    """

    pass


class UserNotFound(BooklyException):
    """
    用户不存在异常类。
    """

    pass


class TagAlreadyExists(BooklyException):
    """
    标签已存在异常类。
    """

    pass


class AccountNotVerified(BooklyException):
    """
    账户未验证异常类。
    """

    pass


# 异步异常处理函数
def create_exception_handler(
    status_code: int, init_detail: Any
) -> Callable[[Request, Exception], JSONResponse]:
    """
    创建异常处理函数。
    """

    async def exception_handler(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(content={"detail": init_detail}, status_code=status_code)

    return exception_handler


def register_error_handlers(app: FastAPI):
    """
    注册异常处理器。
    """

    app.add_exception_handler(
        InvalidToken,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            init_detail={"message": "Invalid token", "error_code": "invalid_token"},
        ),
    )

    app.add_exception_handler(
        RevokedToken,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            init_detail={"message": "Revoked token", "error_code": "revoked_token"},
        ),
    )

    app.add_exception_handler(
        AccessTokenRequired,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            init_detail={
                "message": "Access token required",
                "error_code": "access_token_required",
            },
        ),
    )

    app.add_exception_handler(
        RefreshTokenRequired,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            init_detail={
                "message": "Refresh token required",
                "error_code": "refresh_token_required",
            },
        ),
    )

    app.add_exception_handler(
        UserAlreadyExists,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            init_detail={
                "message": "User with email already exists",
                "error_code": "user_exists",
            },
        ),
    )

    app.add_exception_handler(
        InsufficientPermission,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            init_detail={
                "message": "Insufficient permission",
                "error_code": "insufficient_permission",
            },
        ),
    )

    app.add_exception_handler(
        InvalidCredentials,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            init_detail={
                "message": "Invalid credentials",
                "error_code": "invalid_credentials",
            },
        ),
    )

    app.add_exception_handler(
        BookNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            init_detail={
                "message": "Book not found",
                "error_code": "book_not_found",
            },
        ),
    )

    (
        app.add_exception_handler(
            TagNotFound,
            create_exception_handler(
                status_code=status.HTTP_404_NOT_FOUND,
                init_detail={
                    "message": "Tag not found",
                    "error_code": "tag_not_found",
                },
            ),
        ),
    )

    app.add_exception_handler(
        UserNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            init_detail={
                "message": "User not found",
                "error_code": "user_not_found",
            },
        ),
    )

    app.add_exception_handler(
        TagAlreadyExists,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            init_detail={
                "message": "Tag with name already exists",
                "error_code": "tag_exists",
            },
        ),
    )

    app.add_exception_handler(
        AccountNotVerified,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            init_detail={
                "message": "Account not verified",
                "error_code": "account_not_verified",
                "resolution": "Please check your email for verification details",
            },
        ),
    )

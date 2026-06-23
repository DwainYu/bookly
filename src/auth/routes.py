# 导入路由模块
from src.auth.utils import create_url_safe_token, decode_url_safe_token
from src.config import Config

from fastapi import HTTPException


from src.errors import UserAlreadyExists, UserNotFound, InvalidCredentials, InvalidToken
from datetime import datetime
from fastapi import APIRouter
from src.auth.schemes import (
    UserBooksModel,
    UserModel,
    UserCreateModel,
    UserLoginModel,
    EmailModel,
    PasswordResetRequestModel,
    PasswordResetConfirmModel,
    
)
from src.auth.service import UserService
from src.db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import Depends, status

from src.auth.utils import create_access_token, verify_password,generate_password_hash
from datetime import timedelta
from fastapi.responses import JSONResponse
from src.auth.dependencies import AccessTokenBearer, RefreshTokenBearer
from src.db.redis import add_jti_to_blocklist
from src.auth.dependencies import get_current_user, RoleChecker
from src.celery_tasks import send_email

# 创建路由实例
auth_router = APIRouter()
user_service = UserService()
role_checker = RoleChecker(["admin", "user"])


access_token_bearer = AccessTokenBearer()

REFRESH_EXPIRE_DAYS = 2


@auth_router.post("/send_mail")
async def send_mail(emails: EmailModel):
    recipients = emails.address
    html = "<h1>hello welcome to bookly</h1>"
    subject = "Welcome to Bookly"
    send_email.delay([recipients], subject, html)

    return {"message": "Email sent successfully"}


# 注册端点
@auth_router.post("/signup", status_code=status.HTTP_201_CREATED)
# 注册用户,session: AsyncSession = Depends(get_session) 从依赖项中获取数据库会话对象
async def create_user_Account(
    user_data: UserCreateModel, session: AsyncSession = Depends(get_session)
):
    email = user_data.email
    user_exists = await user_service.user_exists(email, session)
    if user_exists["success"]:
        raise UserAlreadyExists()

    new_user = await user_service.create_user(user_data, session)

    token = create_url_safe_token({"email": email})
    link = f"http://{Config.DOMAIN}/api/v1/auth/verify/{token}"
    html = f"""
    <h1>hello welcome to bookly</h1>
    <p>click the link below to verify your account</p>
    <a href="{link}">{link}</a href>
    """
    subject = "Verify your email"
    send_email.delay([email], subject, html)

    return {
        "message": "Account Created! Check email to verify your account",
        "user": new_user,
    }


@auth_router.post("/verify/{token}")
async def verify_email(token: str, session: AsyncSession = Depends(get_session)):
    # 解码令牌
    token_data = decode_url_safe_token(token)
    user_email = token_data.get("email")

    if user_email:
        user = user_service.get_user_by_email(user_email, session)
        if not user:
            raise UserNotFound()
        # 更新用户状态
        await user_service.update_user(user, {"is_verified": True}, session)
        return JSONResponse(
            content={"message": "Email verified successfully"},
            status_code=status.HTTP_200_OK,
        )
    
    return JSONResponse(
        content={"message": "error, verification failed"},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
    

@auth_router.post(
    "/login", response_model=UserLoginModel, status_code=status.HTTP_200_OK
)
async def login_user(
    login_data: UserLoginModel, session: AsyncSession = Depends(get_session)
):
    email = login_data.email
    password = login_data.password
    user = await user_service.get_user_by_email(email, session)
    if user is not None:
        password_valid = verify_password(password, user.password_hash)
        if password_valid:
            # 创建访问令牌
            access_token = create_access_token(
                user_data={
                    "email": user.email,
                    "user_uid": str(user.uid),
                    "role": user.role,
                }
            )
            # 创建刷新令牌
            refresh_token = create_access_token(
                user_data={
                    "email": user.email,
                    "user_uid": str(user.uid),
                    "role": user.role,
                },
                refresh=True,
                expiry=timedelta(days=REFRESH_EXPIRE_DAYS),
            )
            # 向用户返回jsonresponse，内容是一个字典，包含访问令牌和刷新令牌
            return JSONResponse(
                content={
                    "message": "Login successful",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user": {
                        "email": user.email,
                        "uid": str(user.uid),
                    },
                }
            )
    raise InvalidCredentials()


@auth_router.get("/refresh_token")
async def get_new_refresh_token(token_details: dict = Depends(RefreshTokenBearer())):
    expiry_timestamp = token_details["exp"]
    if datetime.fromtimestamp(expiry_timestamp) > datetime.now():
        new_access_token = create_access_token(user_data=token_details["user"])

        return JSONResponse(
            content={
                "message": "Refresh successful",
                "access_token": new_access_token,
            }
        )

    raise InvalidToken()


@auth_router.get(
    "/me", response_model=UserBooksModel, dependencies=[Depends(role_checker)]
)
async def get_current_user(
    # _:bool = Depends(role_checker)为什么用_？因为_是一个占位符，不使用返回值
    user: UserModel = Depends(get_current_user),
):
    return user


@auth_router.get("/logout")
async def revoke_token(token_details: dict = Depends(AccessTokenBearer())):
    jti = token_details["jti"]
    await add_jti_to_blocklist(jti)
    return JSONResponse(
        content={
            "message": "Logout successful",
        },
        status_code=status.HTTP_200_OK,
    )

@auth_router.post("/password-reset-request")
async def password_reset_request(email_data: PasswordResetRequestModel):
    email = email_data.email

    token = create_url_safe_token({"email": email})

    link = f"http://{Config.DOMAIN}/api/v1/auth/password-reset-confirm/{token}"

    html_message = f"""
    <h1>Reset Your Password</h1>
    <p>Please click this <a href="{link}">link</a> to Reset Your Password</p>
    """
    subject = "Reset Your Password"

    send_email.delay([email], subject, html_message)
    return JSONResponse(
        content={
            "message": "Please check your email for instructions to reset your password",
        },
        status_code=status.HTTP_200_OK,
    )


@auth_router.post("/password-reset-confirm/{token}")
async def reset_account_password(
    token: str,
    passwords: PasswordResetConfirmModel,
    session: AsyncSession = Depends(get_session),
):
    new_password = passwords.new_password
    confirm_password = passwords.confirm_new_password

    if new_password != confirm_password:
        raise HTTPException(
            detail="Passwords do not match", status_code=status.HTTP_400_BAD_REQUEST
        )

    token_data = decode_url_safe_token(token)

    user_email = token_data.get("email")

    if user_email:
        user = await user_service.get_user_by_email(user_email, session)

        if not user:
            raise UserNotFound()

        passwd_hash = generate_password_hash(new_password)
        await user_service.update_user(user, {"password_hash": passwd_hash}, session)

        return JSONResponse(
            content={"message": "Password reset Successfully"},
            status_code=status.HTTP_200_OK,
        )

    return JSONResponse(
        content={"message": "Error occured during password reset."},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
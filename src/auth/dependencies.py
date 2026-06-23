
from src.errors import UserNotFound
from src.db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import Depends
from fastapi import Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .utils import decode_token

from src.db.redis import token_in_blocklist
from .service import UserService
from src.db.models import User
from src.errors import (
    InvalidToken,
    RefreshTokenRequired,
    AccessTokenRequired,
    InsufficientPermission,
    AccountNotVerified,


    )



user_service = UserService()


class TokenBearer(HTTPBearer):
    #重写__init__方法,auto_error默认值为True是为了在没有提供token时返回401错误
    def __init__(self, auto_error: bool = True ):
        #super().__init__(auto_error=auto_error) 调用父类的__init__方法，设置auto_error参数
        # auto_error参数用于指定是否在没有提供token时返回401错误
        super().__init__(auto_error=auto_error)
    # 重写__call__方法，获取请求中的token
    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        """获取请求中的访问令牌"""
        # 调用父类的__call__方法，获取请求中的token
        creds = await super().__call__(request)

        token = creds.credentials
        token_data = decode_token(token)
        
        # 检查token是否有效
        if not self.token_valid(token):
            raise InvalidToken()
        # 检查token是否在黑名单中
        if await token_in_blocklist(token_data['jti']):
            raise InvalidToken()
        self.verify_token_data(token_data)
        return token_data
    
    #为什么参数里有self？
    # 因为self是类的实例，需要在方法中使用self来调用类的其他方法
    def token_valid(self, token: str) -> bool:
        """验证token是否有效"""
        token_data = decode_token(token)
        if token_data is None:
            return False
        else:
            return True
    # 验证令牌数据方法父类
    def verify_token_data(self, token_data: dict) -> bool:
        #重写方法提醒子类实现
        raise NotImplementedError("please override this method in child class")

class AccessTokenBearer(TokenBearer):
    #验证令牌数据方法子类实现
    def verify_token_data(self, token_data: dict) -> bool:
        """验证令牌数据是否有效"""
        if not token_data or token_data['refresh']:
            raise AccessTokenRequired()
        return True

class RefreshTokenBearer(TokenBearer):
    #验证令牌数据方法子类实现
    def verify_token_data(self, token_data: dict) -> bool:
        """验证令牌数据是否有效"""
        if not token_data or not token_data['refresh']:
            raise RefreshTokenRequired()
        return True

async def get_current_user(token_details: dict = Depends(AccessTokenBearer()),session: AsyncSession = Depends(get_session)):
    """获取当前用户"""
    user_email = token_details['user_data']['email']

    user = await user_service.get_user_by_email(user_email, session)

    if user is None:
        raise UserNotFound()
    return user


class RoleChecker:
    def __init__(self, allow_roles: list[str]):
        self.allow_roles = allow_roles
    def __call__(self, current_user: User = Depends(get_current_user)):
        if not current_user.is_verified:
            raise AccountNotVerified()
        if current_user.role not in self.allow_roles:       
            raise InsufficientPermission()
        return True
    


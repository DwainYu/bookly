# 创建与认证相关的实用函数。实用函数的作用是简化认证相关的代码，提高代码的可读性和可维护性。
from itsdangerous import URLSafeTimedSerializer

import logging
import uuid
from passlib.context import CryptContext
import jwt
from datetime import timedelta
    
from src.config import Config
from datetime import datetime

ACCESS_EXPIRE_MINUTES = 3600


# 创建上下文对象，argon2算法，deprecated="auto" 表示自动选择合适的密码哈希算法，
passwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


# 生成密码哈希值
def generate_password_hash(password: str) -> str:
    # 哈希密码
    hash_password = passwd_context.hash(password)
    return hash_password


# 验证密码
def verify_password(password: str, hash_password: str) -> bool:
    # 验证密码
    return passwd_context.verify(password, hash_password)


# 创建访问令牌，刷新令牌用于刷新访问令牌，刷新令牌过期时间为30天，
def create_access_token(user_data: dict, expiry: timedelta = None,refresh: bool = False):
    # 创建 payload 字典，用于存储令牌的负载数据
    payload = {}
    # 将用户数据添加到 payload 字典中
    payload["user_data"] = user_data
    payload["exp"] = datetime.now() + (
        expiry if expiry else timedelta(minutes=ACCESS_EXPIRE_MINUTES)
    )
    payload["jti"] = str(uuid.uuid4())
    payload["refresh"] = refresh
    payload["iat"] = datetime.now()

    # 创建访问令牌
    token = jwt.encode(
        payload=payload,
        key=Config.JWT_SECRET,
        algorithm=Config.JWT_ALGORITHM,
 
    )
    return token

#解码令牌
def decode_token(token: str) -> dict:
    try:
        token_data = jwt.decode(
            jwt=token,
            key=Config.JWT_SECRET,
            algorithms=[Config.JWT_ALGORITHM],
            verify=True,
            options={"verify_iat": False}
        )
        return token_data
    except jwt.PyJWTError as e:
        logging.exception(e)
        return None


serializer = URLSafeTimedSerializer(
    secret_key=Config.JWT_SECRET, salt="email-configuration"
)


def create_url_safe_token(data: dict):
    """创建 URL 安全的签名令牌，用于邮箱验证和密码重置链接"""
    token = serializer.dumps(data)
    return token


def decode_url_safe_token(token: str):
    """解码 URL 安全令牌，如果验证失败则返回 None"""
    try:
        token_data = serializer.loads(token)
        return token_data
    except Exception as e:
        logging.error(str(e))
        return None
        
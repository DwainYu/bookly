import aioredis
from src.config import Config

JTI_EXPIRE = 60 * 60 * 24

#token_blocklist黑名单
# 用于存储已失效的token，防止重复使用
# 作用：
# 1. 存储已失效的token，防止重复使用
# 2. 提供一个全局实例，方便直接使用

#db=0 表示使用第一个数据库
token_blocklist = aioredis.Redis(host=Config.REDIS_HOST, port=Config.REDIS_PORT, db=0)

async def add_jti_to_blocklist(jti: str) -> None:
    """将jti添加到黑名单中"""
    #set方法可以将key-value存储到redis中，key为jti，value为1，过期时间为1天
    await token_blocklist.set(
        name=jti,
        value="",
        ex=JTI_EXPIRE
        
        )
    
async def token_in_blocklist(jti: str) -> bool:
    """检查jti是否在黑名单中"""
    jti = await token_blocklist.exists(jti)
    return bool(jti) 

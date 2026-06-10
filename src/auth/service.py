# 导入数据库模块

from src.auth.schemes import UserCreateModel
from src.db.models import User
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession


class UserService:
    #根据用户邮箱查询用户，self方法表示当前实例对象
    async def get_user_by_email(self, email: str, session: AsyncSession):
        #声明查询语句
        statement = select(User).where(User.email == email) 
        #创建结果对象
        result = await session.exec(statement)
        #返回结果
        user = result.first()

        return user

    #用户存在
    async def user_exists(self, email: str, session: AsyncSession):
        user = await self.get_user_by_email(email, session)
        if user:
            return {
                "success": True,
                "message": "User exists"
            }
        return {
            "success": False,
            "message": "User does not exist"
        }

    #使用客户端的数据创建用户
    async def create_user(self, user_data: UserCreateModel, session: AsyncSession):

        #导入utils中的密码哈希函数
        from src.auth.utils import generate_password_hash

        #将用户数据转换为字典
        # **user_data_dict 表示将字典中的键值对展开为关键字参数
        user_data_dict = user_data.model_dump()

        #哈希密码
        password_hash = generate_password_hash(user_data_dict["password"])

        new_user = User(
            # 从字典中提取用户名、邮箱、密码哈希值
            **user_data_dict,
            password_hash=password_hash,
            is_verified=False,
        )

        #设置用户角色
        new_user.role = "user"

        #添加用户到会话
        session.add(new_user)
        #提交会话
        await session.commit()
        #返回用户
        return new_user
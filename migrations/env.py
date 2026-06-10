import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context
from src.db.models import User
from src.db.models import Book
from sqlmodel import SQLModel
from src.config import Config


database_url = Config.DATABASE_URL

# 这是 Alembic Config 对象，用于访问 .ini 文件中的配置值
# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config
config.set_main_option("sqlalchemy.url", database_url)

# 解析配置文件以设置 Python 日志
# 这行代码主要用于设置日志记录器
# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 在这里添加模型的 MetaData 对象以支持 'autogenerate' 功能
# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = SQLModel.metadata

# 来自配置的其他值，由 env.py 的需求定义
# 可以通过以下方式获取：
# my_important_option = config.get_main_option("my_important_option")
# ... 以此类推
# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """在 'offline' 模式下运行迁移

    此配置使用仅 URL 来配置上下文，而不是 Engine，
    但 Engine 也是可以接受的。通过跳过 Engine 创建，
    我们甚至不需要 DBAPI 可用。

    在这里对 context.execute() 的调用会将给定字符串输出到脚本

    """
    # Run migrations in 'offline' mode.
    # This configures the context with just a URL
    # and not an Engine, though an Engine is acceptable
    # here as well.  By skipping the Engine creation
    # we don't even need a DBAPI to be available.
    # Calls to context.execute() here emit the given string to the
    # script output.
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """在这个场景中，我们需要创建一个 Engine
    并将连接与上下文关联

    """
    # In this scenario we need to create an Engine
    # and associate a connection with the context.
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """在 'online' 模式下运行迁移"""
    # Run migrations in 'online' mode.
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

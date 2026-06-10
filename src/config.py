from pydantic_settings import BaseSettings, SettingsConfigDict

# Settings 类，用于存储环境变量。作用：
# 1. 从 .env 文件中读取环境变量
# 2. 提供一个全局实例，方便直接使用
# 3. 提供一个模型，用于存储环境变量
class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"

    )

# 创建全局实例，方便直接使用
Config = Settings()
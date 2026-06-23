from pydantic_settings import BaseSettings, SettingsConfigDict

# Settings 类，用于存储环境变量。作用：
# 1. 从 .env 文件中读取环境变量
# 2. 提供一个全局实例，方便直接使用
# 3. 提供一个模型，用于存储环境变量
class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str
    REDIS_URL: str = "redis://localhost:6379/0"
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_FROM_NAME: str
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True
    DOMAIN: str
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"

    )

# 创建全局实例，方便直接使用
Config = Settings()

broker_url = Config.REDIS_URL
result_backend = Config.REDIS_URL
broker_connection_retry_on_startup = True

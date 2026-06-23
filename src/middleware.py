from fastapi import FastAPI, Request
from time import time
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.cors import CORSMiddleware
import logging


logger = logging.getLogger("unicorn.access")
# 禁用日志记录
logger.disabled = True


def register_middleware(app: FastAPI):
    """
    注册中间件。
    """

    @app.middleware("http")
    async def custom_logging(request: Request, call_next):
        """
        自定义日志中间件。
        """
        start_time = time()

        response = await call_next(request)

        end_time = time()
        duration = end_time - start_time
        message = f"Request: {request.method} - {request.url.path} | Duration: {duration:.4f} seconds"
        logger.info(message)
        print(message)

        return response

    # 添加CORS中间件:跨源资源共享,允许所有来源,允许所有请求方法,允许所有请求头
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    

    #添加可信任主机中间件
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1"],
    )
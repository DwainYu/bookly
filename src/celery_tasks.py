from celery import Celery
from src.mail import mail, create_message
from asgiref.sync import async_to_sync

# 创建 Celery 应用实例，用于异步任务调度
c_app = Celery()

# 从配置模块加载 Celery 设置
c_app.config_from_object("src.config")


@c_app.task()
def send_email(recipients: list[str], subject: str, body: str):
    """异步发送邮件任务，通过 FastMail 发送 HTML 邮件"""

    message = create_message(recipients=recipients, subject=subject, body=body)

    # 使用 async_to_sync 将异步函数转换为同步函数并执行, 避免阻塞事件循环, 使邮件发送在后台异步进行
    async_to_sync(mail.send_message)(message)
    print("Email sent")

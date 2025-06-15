from tortoise.models import Model
from tortoise import fields
from datetime import datetime


class SystemLog(Model):
    """系统日志模型"""
    id = fields.IntField(pk=True)
    level = fields.CharField(max_length=20, description="日志级别")  # info, warning, error, debug
    module = fields.CharField(max_length=50, description="模块名称")  # auth, questions, system, upload
    message = fields.TextField(description="日志消息")
    details = fields.JSONField(null=True, description="详细信息")
    user = fields.CharField(max_length=100, null=True, description="操作用户")
    ip_address = fields.CharField(max_length=45, null=True, description="IP地址")
    user_agent = fields.CharField(max_length=500, null=True, description="用户代理")
    request_id = fields.CharField(max_length=100, null=True, description="请求ID")
    timestamp = fields.DatetimeField(auto_now_add=True, description="时间戳")
    
    class Meta:
        table = "system_logs"
        ordering = ["-timestamp"]
    
    def __str__(self):
        return f"[{self.level.upper()}] {self.module}: {self.message}"


class LogLevel:
    """日志级别常量"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class LogModule:
    """日志模块常量"""
    AUTH = "auth"
    QUESTIONS = "questions"
    SYSTEM = "system"
    UPLOAD = "upload"
    TEMPLATES = "templates"
    ANALYTICS = "analytics"

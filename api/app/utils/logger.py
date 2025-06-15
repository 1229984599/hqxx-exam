import json
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import Request
from app.models.system_log import SystemLog, LogLevel, LogModule


class SystemLogger:
    """系统日志记录器"""
    
    @staticmethod
    async def log(
        level: str,
        module: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        user: Optional[str] = None,
        request: Optional[Request] = None,
        request_id: Optional[str] = None
    ):
        """记录系统日志"""
        try:
            # 从请求中提取信息
            ip_address = None
            user_agent = None
            
            if request:
                ip_address = request.client.host if request.client else None
                user_agent = request.headers.get("user-agent")
                if not request_id:
                    request_id = str(uuid.uuid4())
            
            # 创建日志记录
            await SystemLog.create(
                level=level,
                module=module,
                message=message,
                details=details,
                user=user,
                ip_address=ip_address,
                user_agent=user_agent,
                request_id=request_id
            )
        except Exception as e:
            # 日志记录失败时，至少打印到控制台
            print(f"Failed to log to database: {e}")
            print(f"[{level.upper()}] {module}: {message}")
    
    @staticmethod
    async def debug(module: str, message: str, **kwargs):
        """记录调试日志"""
        await SystemLogger.log(LogLevel.DEBUG, module, message, **kwargs)
    
    @staticmethod
    async def info(module: str, message: str, **kwargs):
        """记录信息日志"""
        await SystemLogger.log(LogLevel.INFO, module, message, **kwargs)
    
    @staticmethod
    async def warning(module: str, message: str, **kwargs):
        """记录警告日志"""
        await SystemLogger.log(LogLevel.WARNING, module, message, **kwargs)
    
    @staticmethod
    async def error(module: str, message: str, **kwargs):
        """记录错误日志"""
        await SystemLogger.log(LogLevel.ERROR, module, message, **kwargs)
    
    @staticmethod
    async def auth_login(username: str, success: bool, request: Optional[Request] = None):
        """记录登录日志"""
        level = LogLevel.INFO if success else LogLevel.WARNING
        message = f"用户 {username} 登录{'成功' if success else '失败'}"
        await SystemLogger.log(
            level=level,
            module=LogModule.AUTH,
            message=message,
            user=username if success else None,
            request=request
        )
    
    @staticmethod
    async def auth_logout(username: str, request: Optional[Request] = None):
        """记录登出日志"""
        await SystemLogger.log(
            level=LogLevel.INFO,
            module=LogModule.AUTH,
            message=f"用户 {username} 登出",
            user=username,
            request=request
        )
    
    @staticmethod
    async def question_created(question_id: int, title: str, user: str, request: Optional[Request] = None):
        """记录试题创建日志"""
        await SystemLogger.log(
            level=LogLevel.INFO,
            module=LogModule.QUESTIONS,
            message=f"创建试题: {title}",
            details={"question_id": question_id, "title": title},
            user=user,
            request=request
        )
    
    @staticmethod
    async def question_updated(question_id: int, title: str, user: str, request: Optional[Request] = None):
        """记录试题更新日志"""
        await SystemLogger.log(
            level=LogLevel.INFO,
            module=LogModule.QUESTIONS,
            message=f"更新试题: {title}",
            details={"question_id": question_id, "title": title},
            user=user,
            request=request
        )
    
    @staticmethod
    async def question_deleted(question_id: int, title: str, user: str, request: Optional[Request] = None):
        """记录试题删除日志"""
        await SystemLogger.log(
            level=LogLevel.WARNING,
            module=LogModule.QUESTIONS,
            message=f"删除试题: {title}",
            details={"question_id": question_id, "title": title},
            user=user,
            request=request
        )
    
    @staticmethod
    async def batch_operation(operation: str, count: int, user: str, request: Optional[Request] = None):
        """记录批量操作日志"""
        await SystemLogger.log(
            level=LogLevel.INFO,
            module=LogModule.QUESTIONS,
            message=f"批量{operation}: {count}个项目",
            details={"operation": operation, "count": count},
            user=user,
            request=request
        )
    
    @staticmethod
    async def file_uploaded(filename: str, size: int, user: str, request: Optional[Request] = None):
        """记录文件上传日志"""
        await SystemLogger.log(
            level=LogLevel.INFO,
            module=LogModule.UPLOAD,
            message=f"上传文件: {filename}",
            details={"filename": filename, "size": size},
            user=user,
            request=request
        )
    
    @staticmethod
    async def system_backup(backup_id: str, user: str, request: Optional[Request] = None):
        """记录系统备份日志"""
        await SystemLogger.log(
            level=LogLevel.INFO,
            module=LogModule.SYSTEM,
            message=f"创建系统备份: {backup_id}",
            details={"backup_id": backup_id},
            user=user,
            request=request
        )
    
    @staticmethod
    async def admin_created(admin_username: str, creator: str, request: Optional[Request] = None):
        """记录管理员创建日志"""
        await SystemLogger.log(
            level=LogLevel.INFO,
            module=LogModule.SYSTEM,
            message=f"创建管理员账户: {admin_username}",
            details={"admin_username": admin_username},
            user=creator,
            request=request
        )
    
    @staticmethod
    async def admin_deleted(admin_username: str, deleter: str, request: Optional[Request] = None):
        """记录管理员删除日志"""
        await SystemLogger.log(
            level=LogLevel.WARNING,
            module=LogModule.SYSTEM,
            message=f"删除管理员账户: {admin_username}",
            details={"admin_username": admin_username},
            user=deleter,
            request=request
        )

#!/usr/bin/env python3
"""
创建示例系统日志数据
用于测试和演示系统日志功能
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
import random

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tortoise import Tortoise
from app.models.system_log import SystemLog, LogLevel, LogModule
from app.config import settings


async def create_sample_logs():
    """创建示例日志数据"""
    
    # 初始化数据库连接
    await Tortoise.init(
        db_url=settings.DATABASE_URL,
        modules={"models": ["app.models"]}
    )
    
    print("开始创建示例日志数据...")
    
    # 定义示例日志数据
    sample_logs = [
        # 认证模块日志
        {
            "level": LogLevel.INFO,
            "module": LogModule.AUTH,
            "message": "用户 admin 登录成功",
            "user": "admin",
            "ip_address": "127.0.0.1"
        },
        {
            "level": LogLevel.WARNING,
            "module": LogModule.AUTH,
            "message": "用户 test 登录失败：密码错误",
            "user": "test",
            "ip_address": "192.168.1.100"
        },
        {
            "level": LogLevel.INFO,
            "module": LogModule.AUTH,
            "message": "用户 admin 刷新令牌成功",
            "user": "admin",
            "ip_address": "127.0.0.1"
        },
        
        # 试题模块日志
        {
            "level": LogLevel.INFO,
            "module": LogModule.QUESTIONS,
            "message": "创建试题成功",
            "details": {"question_id": 1, "title": "数学基础题"},
            "user": "admin"
        },
        {
            "level": LogLevel.INFO,
            "module": LogModule.QUESTIONS,
            "message": "批量更新试题完成",
            "details": {"updated_count": 5},
            "user": "admin"
        },
        {
            "level": LogLevel.WARNING,
            "module": LogModule.QUESTIONS,
            "message": "试题删除操作：权限不足",
            "user": "teacher"
        },
        
        # 系统模块日志
        {
            "level": LogLevel.INFO,
            "module": LogModule.SYSTEM,
            "message": "系统启动完成",
            "details": {"startup_time": "2.5s"}
        },
        {
            "level": LogLevel.ERROR,
            "module": LogModule.SYSTEM,
            "message": "数据库连接失败",
            "details": {"error": "Connection timeout"}
        },
        {
            "level": LogLevel.INFO,
            "module": LogModule.SYSTEM,
            "message": "系统备份完成",
            "details": {"backup_size": "15.2MB"}
        },
        {
            "level": LogLevel.WARNING,
            "module": LogModule.SYSTEM,
            "message": "磁盘空间不足警告",
            "details": {"available_space": "1.2GB"}
        },
        
        # 上传模块日志
        {
            "level": LogLevel.INFO,
            "module": LogModule.UPLOAD,
            "message": "文件上传成功",
            "details": {"filename": "image.jpg", "size": "2.1MB"},
            "user": "admin"
        },
        {
            "level": LogLevel.ERROR,
            "module": LogModule.UPLOAD,
            "message": "文件上传失败：文件过大",
            "details": {"filename": "large_file.pdf", "size": "50MB"},
            "user": "teacher"
        },
        
        # 模板模块日志
        {
            "level": LogLevel.INFO,
            "module": LogModule.TEMPLATES,
            "message": "创建模板成功",
            "details": {"template_name": "数学练习模板"},
            "user": "admin"
        },
        {
            "level": LogLevel.INFO,
            "module": LogModule.TEMPLATES,
            "message": "模板应用到试题",
            "details": {"template_id": 1, "question_count": 3},
            "user": "teacher"
        },
        
        # 分析模块日志
        {
            "level": LogLevel.INFO,
            "module": LogModule.ANALYTICS,
            "message": "生成数据分析报告",
            "details": {"report_type": "monthly", "data_points": 1250},
            "user": "admin"
        }
    ]
    
    # 创建日志记录，分布在过去30天内
    created_count = 0
    base_time = datetime.now()
    
    for i in range(100):  # 创建100条日志记录
        # 随机选择一个示例日志
        sample = random.choice(sample_logs)
        
        # 随机生成时间（过去30天内）
        days_ago = random.randint(0, 30)
        hours_ago = random.randint(0, 23)
        minutes_ago = random.randint(0, 59)
        
        timestamp = base_time - timedelta(
            days=days_ago,
            hours=hours_ago,
            minutes=minutes_ago
        )
        
        # 创建日志记录
        await SystemLog.create(
            level=sample["level"],
            module=sample["module"],
            message=sample["message"],
            details=sample.get("details"),
            user=sample.get("user"),
            ip_address=sample.get("ip_address", "127.0.0.1"),
            timestamp=timestamp
        )
        
        created_count += 1
        
        if created_count % 20 == 0:
            print(f"已创建 {created_count} 条日志记录...")
    
    print(f"示例日志数据创建完成！总共创建了 {created_count} 条记录")
    
    # 统计各级别日志数量
    info_count = await SystemLog.filter(level=LogLevel.INFO).count()
    warning_count = await SystemLog.filter(level=LogLevel.WARNING).count()
    error_count = await SystemLog.filter(level=LogLevel.ERROR).count()
    
    print(f"日志统计：")
    print(f"  信息日志：{info_count} 条")
    print(f"  警告日志：{warning_count} 条")
    print(f"  错误日志：{error_count} 条")
    
    # 关闭数据库连接
    await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(create_sample_logs())

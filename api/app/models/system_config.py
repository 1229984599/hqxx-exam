from tortoise.models import Model
from tortoise import fields
from datetime import datetime


class SystemConfig(Model):
    """系统配置模型"""
    id = fields.IntField(pk=True)
    config_key = fields.CharField(max_length=100, unique=True, description="配置键")
    config_value = fields.TextField(description="配置值")
    config_type = fields.CharField(max_length=50, description="配置类型")  # backup, system, security, file, email
    description = fields.CharField(max_length=500, null=True, description="配置描述")
    is_active = fields.BooleanField(default=True, description="是否启用")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")
    updated_by = fields.CharField(max_length=100, null=True, description="更新者")
    
    class Meta:
        table = "system_configs"
        ordering = ["config_type", "config_key"]
    
    def __str__(self):
        return f"{self.config_type}.{self.config_key}"


class ConfigType:
    """配置类型常量"""
    BACKUP = "backup"
    SYSTEM = "system"
    SECURITY = "security"
    FILE = "file"
    EMAIL = "email"


class ConfigKey:
    """配置键常量"""
    # 备份配置
    BACKUP_METHOD = "backup.method"
    BACKUP_AUTO = "backup.auto"
    BACKUP_WEBDAV = "backup.webdav"
    BACKUP_FTP = "backup.ftp"
    
    # 系统配置
    SYSTEM_BASIC = "system.basic"
    SYSTEM_SECURITY = "system.security"
    SYSTEM_FILE = "system.file"
    SYSTEM_EMAIL = "system.email"

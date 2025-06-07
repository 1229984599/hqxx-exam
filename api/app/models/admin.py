from tortoise import fields
from .base import BaseModel


class Admin(BaseModel):
    """管理员模型"""
    username = fields.CharField(max_length=50, unique=True, description="用户名")
    email = fields.CharField(max_length=100, unique=True, description="邮箱")
    hashed_password = fields.CharField(max_length=255, description="密码哈希")
    full_name = fields.CharField(max_length=100, null=True, description="姓名")
    is_active = fields.BooleanField(default=True, description="是否激活")
    is_superuser = fields.BooleanField(default=False, description="是否超级管理员")
    
    class Meta:
        table = "admins"
        table_description = "管理员表"
    
    def __str__(self):
        return self.username

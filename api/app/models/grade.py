from tortoise import fields
from .base import BaseModel


class Grade(BaseModel):
    """年级模型"""
    name = fields.CharField(max_length=50, unique=True, description="年级名称")
    code = fields.CharField(max_length=20, unique=True, description="年级代码")
    level = fields.IntField(description="年级级别")
    is_active = fields.BooleanField(default=True, description="是否激活")
    sort_order = fields.IntField(default=0, description="排序")
    description = fields.TextField(null=True, description="描述")
    
    class Meta:
        table = "grades"
        table_description = "年级表"
        ordering = ["sort_order", "level"]
    
    def __str__(self):
        return self.name

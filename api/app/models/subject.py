from tortoise import fields
from .base import BaseModel


class Subject(BaseModel):
    """学科模型"""
    name = fields.CharField(max_length=50, unique=True, description="学科名称")
    code = fields.CharField(max_length=20, unique=True, description="学科代码")
    icon = fields.CharField(max_length=100, null=True, description="图标")
    color = fields.CharField(max_length=20, null=True, description="颜色")
    is_active = fields.BooleanField(default=True, description="是否激活")
    sort_order = fields.IntField(default=0, description="排序")
    description = fields.TextField(null=True, description="描述")
    
    class Meta:
        table = "subjects"
        table_description = "学科表"
        ordering = ["sort_order", "id"]
    
    def __str__(self):
        return self.name

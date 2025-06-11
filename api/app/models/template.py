from tortoise import fields
from .base import BaseModel


class Template(BaseModel):
    """模板模型"""
    name = fields.CharField(max_length=100, description="模板名称")
    description = fields.CharField(max_length=500, null=True, description="模板描述")
    content = fields.TextField(description="模板内容(HTML)")
    category = fields.CharField(max_length=50, description="模板分类")
    icon = fields.CharField(max_length=20, null=True, description="模板图标")
    
    # 关联字段
    subject = fields.ForeignKeyField("models.Subject", related_name="templates", null=True, description="适用学科")
    
    # 状态字段
    is_active = fields.BooleanField(default=True, description="是否激活")
    is_system = fields.BooleanField(default=False, description="是否系统模板")
    sort_order = fields.IntField(default=0, description="排序")
    
    # 使用统计
    usage_count = fields.IntField(default=0, description="使用次数")
    
    class Meta:
        table = "templates"
        table_description = "模板表"
        ordering = ["sort_order", "-created_at"]
    
    def __str__(self):
        return self.name

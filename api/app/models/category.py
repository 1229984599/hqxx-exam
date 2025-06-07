from tortoise import fields
from .base import BaseModel


class Category(BaseModel):
    """题目分类模型"""
    name = fields.CharField(max_length=100, description="分类名称")
    code = fields.CharField(max_length=50, description="分类代码")
    subject = fields.ForeignKeyField("models.Subject", related_name="categories", description="所属学科")
    parent = fields.ForeignKeyField("models.Category", related_name="children", null=True, description="父分类")
    level = fields.IntField(default=1, description="分类级别")
    is_active = fields.BooleanField(default=True, description="是否激活")
    sort_order = fields.IntField(default=0, description="排序")
    description = fields.TextField(null=True, description="描述")
    
    class Meta:
        table = "categories"
        table_description = "题目分类表"
        ordering = ["sort_order", "id"]
        unique_together = (("subject", "code"),)
    
    def __str__(self):
        return f"{self.subject.name} - {self.name}"

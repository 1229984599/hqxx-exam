from tortoise import fields
from .base import BaseModel


class Semester(BaseModel):
    """学期模型"""
    name = fields.CharField(max_length=50, unique=True, description="学期名称")
    code = fields.CharField(max_length=20, unique=True, description="学期代码")
    start_date = fields.DateField(null=True, description="开始日期")
    end_date = fields.DateField(null=True, description="结束日期")
    is_active = fields.BooleanField(default=True, description="是否激活")
    sort_order = fields.IntField(default=0, description="排序")
    description = fields.TextField(null=True, description="描述")
    
    class Meta:
        table = "semesters"
        table_description = "学期表"
        ordering = ["sort_order", "id"]
    
    def __str__(self):
        return self.name

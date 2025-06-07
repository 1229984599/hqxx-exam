from tortoise.models import Model
from tortoise import fields


class BaseModel(Model):
    """基础模型类"""
    id = fields.IntField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")
    
    class Meta:
        abstract = True

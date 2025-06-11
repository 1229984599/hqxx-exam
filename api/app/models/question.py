from tortoise import fields
from .base import BaseModel


class Question(BaseModel):
    """试题模型"""
    title = fields.CharField(max_length=200, description="题目标题")
    content = fields.TextField(description="题目内容(富文本)")
    answer = fields.TextField(null=True, description="参考答案(富文本)")

    difficulty = fields.IntField(default=1, description="难度等级(1-5)")
    question_type = fields.CharField(max_length=20, default="single", description="题目类型")
    
    # 关联字段
    semester = fields.ForeignKeyField("models.Semester", related_name="questions", description="学期")
    grade = fields.ForeignKeyField("models.Grade", related_name="questions", description="年级")
    subject = fields.ForeignKeyField("models.Subject", related_name="questions", description="学科")
    category = fields.ForeignKeyField("models.Category", related_name="questions", description="分类")
    
    # 状态字段
    is_active = fields.BooleanField(default=True, description="是否激活")
    is_published = fields.BooleanField(default=False, description="是否发布")
    view_count = fields.IntField(default=0, description="查看次数")
    
    # 元数据
    tags = fields.CharField(max_length=200, null=True, description="标签(逗号分隔)")
    source = fields.CharField(max_length=100, null=True, description="题目来源")
    author = fields.CharField(max_length=50, null=True, description="出题人")
    
    class Meta:
        table = "questions"
        table_description = "试题表"
        ordering = ["-created_at"]
    
    def __str__(self):
        return self.title

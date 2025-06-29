from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime


class BaseResponse(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PaginationParams(BaseModel):
    page: int = 1
    size: int = 20


class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int


class MessageResponse(BaseModel):
    message: str


# 批量操作相关Schema
class BatchUpdateRequest(BaseModel):
    ids: Optional[List[int]] = None
    semester_ids: Optional[List[int]] = None
    grade_ids: Optional[List[int]] = None
    subject_ids: Optional[List[int]] = None
    category_ids: Optional[List[int]] = None
    admin_ids: Optional[List[int]] = None
    update_data: dict

    def get_ids(self) -> List[int]:
        """获取实际的ID列表"""
        for field_name in ['ids', 'semester_ids', 'grade_ids', 'subject_ids', 'category_ids', 'admin_ids']:
            ids = getattr(self, field_name, None)
            if ids:
                return ids
        return []


class BatchDeleteRequest(BaseModel):
    ids: Optional[List[int]] = None
    semester_ids: Optional[List[int]] = None
    grade_ids: Optional[List[int]] = None
    subject_ids: Optional[List[int]] = None
    category_ids: Optional[List[int]] = None
    admin_ids: Optional[List[int]] = None

    def get_ids(self) -> List[int]:
        """获取实际的ID列表"""
        for field_name in ['ids', 'semester_ids', 'grade_ids', 'subject_ids', 'category_ids', 'admin_ids']:
            ids = getattr(self, field_name, None)
            if ids:
                return ids
        return []


class BatchCopyRequest(BaseModel):
    ids: Optional[List[int]] = None
    semester_ids: Optional[List[int]] = None
    grade_ids: Optional[List[int]] = None
    subject_ids: Optional[List[int]] = None
    category_ids: Optional[List[int]] = None
    copy_data: dict

    def get_ids(self) -> List[int]:
        """获取实际的ID列表"""
        for field_name in ['ids', 'semester_ids', 'grade_ids', 'subject_ids', 'category_ids']:
            ids = getattr(self, field_name, None)
            if ids:
                return ids
        return []


class BatchOperationResponse(BaseModel):
    success_count: int
    failed_count: int = 0
    total_count: int
    message: str
    failed_items: List[dict] = []


class SemesterBase(BaseModel):
    name: str
    code: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_active: bool = True
    sort_order: int = 0
    description: Optional[str] = None


class SemesterCreate(SemesterBase):
    pass


class SemesterUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None
    description: Optional[str] = None


class SemesterResponse(BaseResponse, SemesterBase):
    pass


class GradeBase(BaseModel):
    name: str
    code: str
    level: int
    is_active: bool = True
    sort_order: int = 0
    description: Optional[str] = None


class GradeCreate(GradeBase):
    pass


class GradeUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    level: Optional[int] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None
    description: Optional[str] = None


class GradeResponse(BaseResponse, GradeBase):
    pass


class SubjectBase(BaseModel):
    name: str
    code: str
    icon: Optional[str] = None
    color: Optional[str] = None
    is_active: bool = True
    sort_order: int = 0
    description: Optional[str] = None


class SubjectCreate(SubjectBase):
    pass


class SubjectUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None
    description: Optional[str] = None


class SubjectResponse(BaseResponse, SubjectBase):
    pass


class CategoryBase(BaseModel):
    name: str
    code: str
    subject_id: int
    parent_id: Optional[int] = None
    level: int = 1
    is_active: bool = True
    sort_order: int = 0
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    subject_id: Optional[int] = None
    parent_id: Optional[int] = None
    level: Optional[int] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None
    description: Optional[str] = None


class CategoryResponse(BaseResponse):
    name: str
    code: str
    subject_id: int
    parent_id: Optional[int] = None
    level: int = 1
    is_active: bool = True
    sort_order: int = 0
    description: Optional[str] = None
    subject: Optional[SubjectResponse] = None
    parent: Optional["CategoryResponse"] = None
    children: List["CategoryResponse"] = []


class QuestionBase(BaseModel):
    title: str
    content: str
    answer: Optional[str] = None
    difficulty: int = 1
    question_type: str = "single"
    semester_id: int
    grade_id: int
    subject_id: int
    category_id: int
    is_active: bool = True
    is_published: bool = False
    tags: Optional[str] = None
    source: Optional[str] = None
    author: Optional[str] = None


class QuestionCreate(QuestionBase):
    pass


class QuestionUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    answer: Optional[str] = None
    difficulty: Optional[int] = None
    question_type: Optional[str] = None
    semester_id: Optional[int] = None
    grade_id: Optional[int] = None
    subject_id: Optional[int] = None
    category_id: Optional[int] = None
    is_active: Optional[bool] = None
    is_published: Optional[bool] = None
    tags: Optional[str] = None
    source: Optional[str] = None
    author: Optional[str] = None


class QuestionResponse(BaseResponse):
    title: str
    content: str
    answer: Optional[str] = None
    difficulty: int = 1
    question_type: str = "single"
    semester_id: int
    grade_id: int
    subject_id: int
    category_id: int
    is_active: bool = True
    is_published: bool = False
    tags: Optional[str] = None
    source: Optional[str] = None
    author: Optional[str] = None
    view_count: int
    semester: Optional[SemesterResponse] = None
    grade: Optional[GradeResponse] = None
    subject: Optional[SubjectResponse] = None
    category: Optional[CategoryResponse] = None


class TemplateBase(BaseModel):
    name: str
    description: Optional[str] = None
    content: str
    category: str
    icon: Optional[str] = None
    subject_id: Optional[int] = None
    is_active: bool = True
    is_system: bool = False
    sort_order: int = 0


class TemplateCreate(TemplateBase):
    pass


class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    icon: Optional[str] = None
    subject_id: Optional[int] = None
    is_active: Optional[bool] = None
    is_system: Optional[bool] = None
    sort_order: Optional[int] = None


class TemplateResponse(BaseResponse):
    name: str
    description: Optional[str] = None
    content: str
    category: str
    icon: Optional[str] = None
    subject_id: Optional[int] = None
    is_active: bool = True
    is_system: bool = False
    sort_order: int = 0
    usage_count: int = 0
    subject: Optional[SubjectResponse] = None





# 解决循环引用
CategoryResponse.model_rebuild()

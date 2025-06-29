import random
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from app.models.question import Question
from app.models.semester import Semester
from app.models.grade import Grade
from app.models.subject import Subject
from app.models.category import Category
from app.schemas.common import (
    QuestionCreate, QuestionUpdate, QuestionResponse,
    MessageResponse
)
from app.dependencies.auth import get_current_active_admin
from app.utils.permissions import PermissionManager
from app.models.role import PermissionCode, RoleCode
from pydantic import BaseModel

router = APIRouter(prefix="/questions", tags=["试题管理"])


@router.get("/", summary="获取试题列表")
async def get_questions(
    semester_id: int = Query(None, description="学期ID"),
    grade_id: int = Query(None, description="年级ID"),
    subject_id: int = Query(None, description="学科ID"),
    category_id: int = Query(None, description="分类ID"),
    is_active: bool = Query(None, description="是否激活"),
    is_published: bool = Query(None, description="是否发布"),
    difficulty: int = Query(None, ge=1, le=5, description="难度等级"),
    question_type: str = Query(None, description="题目类型"),
    search: str = Query(None, description="搜索关键词"),
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(20, ge=1, le=100, description="限制数量"),
    current_admin = Depends(get_current_active_admin)
):
    """获取试题列表"""
    # 检查角色：教师及以上角色可以查看试题
    if not current_admin.is_superuser and not await PermissionManager.has_any_role(current_admin, [RoleCode.SUPER_ADMIN, RoleCode.ADMIN, RoleCode.TEACHER, RoleCode.SUBJECT_ADMIN]):
        raise HTTPException(status_code=403, detail="Role required: teacher or above")
    query = Question.all().prefetch_related("semester", "grade", "subject", "category")

    if semester_id is not None:
        query = query.filter(semester_id=semester_id)

    if grade_id is not None:
        query = query.filter(grade_id=grade_id)

    if subject_id is not None:
        query = query.filter(subject_id=subject_id)

    if category_id is not None:
        query = query.filter(category_id=category_id)

    if is_active is not None:
        query = query.filter(is_active=is_active)

    if is_published is not None:
        query = query.filter(is_published=is_published)

    if difficulty is not None:
        query = query.filter(difficulty=difficulty)

    if question_type:
        query = query.filter(question_type=question_type)

    if search:
        query = query.filter(title__icontains=search)

    # 获取总数（在分页之前）
    total = await query.count()

    # 执行分页查询
    questions = await query.offset(skip).limit(limit).order_by("-created_at")

    # 手动序列化避免循环引用
    result = []
    for question in questions:
        question_dict = {
            "id": question.id,
            "title": question.title,
            "content": question.content,
            "answer": question.answer,
            "difficulty": question.difficulty,
            "question_type": question.question_type,
            "semester_id": question.semester_id,
            "grade_id": question.grade_id,
            "subject_id": question.subject_id,
            "category_id": question.category_id,
            "is_active": question.is_active,
            "is_published": question.is_published,
            "tags": question.tags,
            "source": question.source,
            "author": question.author,
            "view_count": question.view_count,
            "created_at": question.created_at,
            "updated_at": question.updated_at,
            "semester": {
                "id": question.semester.id,
                "name": question.semester.name,
                "code": question.semester.code
            } if question.semester else None,
            "grade": {
                "id": question.grade.id,
                "name": question.grade.name,
                "code": question.grade.code
            } if question.grade else None,
            "subject": {
                "id": question.subject.id,
                "name": question.subject.name,
                "code": question.subject.code
            } if question.subject else None,
            "category": {
                "id": question.category.id,
                "name": question.category.name,
                "code": question.category.code
            } if question.category else None
        }
        result.append(question_dict)

    # 返回分页格式的数据
    return {
        "items": result,
        "total": total,
        "page": (skip // limit) + 1,
        "size": limit,
        "pages": (total + limit - 1) // limit  # 总页数
    }


@router.get("/random", summary="随机获取试题")
async def get_random_question(
    semester_id: int = Query(..., description="学期ID"),
    grade_id: int = Query(..., description="年级ID"),
    subject_id: int = Query(..., description="学科ID"),
    category_id: int = Query(..., description="分类ID"),
    difficulty: int = Query(None, ge=1, le=5, description="难度等级"),
    exclude_ids: str = Query(None, description="排除的题目ID列表，逗号分隔")
):
    """随机获取一道试题"""
    query = Question.filter(
        semester_id=semester_id,
        grade_id=grade_id,
        subject_id=subject_id,
        category_id=category_id,
        is_active=True,
        is_published=True
    ).prefetch_related("semester", "grade", "subject", "category")

    if difficulty is not None:
        query = query.filter(difficulty=difficulty)

    if exclude_ids:
        exclude_list = [int(x.strip()) for x in exclude_ids.split(",") if x.strip().isdigit()]
        if exclude_list:
            query = query.exclude(id__in=exclude_list)

    questions = await query.all()

    if not questions:
        raise HTTPException(status_code=404, detail="No questions found")

    # 随机选择一道题目
    question = random.choice(questions)

    # 增加查看次数
    question.view_count += 1
    await question.save()

    return {
        "id": question.id,
        "title": question.title,
        "content": question.content,
        "answer": question.answer,
        "difficulty": question.difficulty,
        "question_type": question.question_type,
        "semester_id": question.semester_id,
        "grade_id": question.grade_id,
        "subject_id": question.subject_id,
        "category_id": question.category_id,
        "is_active": question.is_active,
        "is_published": question.is_published,
        "tags": question.tags,
        "source": question.source,
        "author": question.author,
        "view_count": question.view_count,
        "created_at": question.created_at,
        "updated_at": question.updated_at,
        "semester": {
            "id": question.semester.id,
            "name": question.semester.name,
            "code": question.semester.code
        } if question.semester else None,
        "grade": {
            "id": question.grade.id,
            "name": question.grade.name,
            "code": question.grade.code
        } if question.grade else None,
        "subject": {
            "id": question.subject.id,
            "name": question.subject.name,
            "code": question.subject.code
        } if question.subject else None,
        "category": {
            "id": question.category.id,
            "name": question.category.name,
            "code": question.category.code
        } if question.category else None
    }


@router.get("/{question_id}", summary="获取试题详情")
async def get_question(
    question_id: int,
    current_admin = Depends(get_current_active_admin)
):
    """获取试题详情"""
    # 检查权限
    if not current_admin.is_superuser and not await PermissionManager.has_permission(current_admin, PermissionCode.QUESTIONS_VIEW):
        raise HTTPException(status_code=403, detail="Permission denied")
    question = await Question.filter(id=question_id).prefetch_related(
        "semester", "grade", "subject", "category"
    ).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    # 增加查看次数
    question.view_count += 1
    await question.save()

    # 返回与列表API一致的格式
    return {
        "id": question.id,
        "title": question.title,
        "content": question.content,
        "answer": question.answer,
        "difficulty": question.difficulty,
        "question_type": question.question_type,
        "semester_id": question.semester_id,
        "grade_id": question.grade_id,
        "subject_id": question.subject_id,
        "category_id": question.category_id,
        "is_active": question.is_active,
        "is_published": question.is_published,
        "tags": question.tags,
        "source": question.source,
        "author": question.author,
        "view_count": question.view_count,
        "created_at": question.created_at,
        "updated_at": question.updated_at,
        "semester": {
            "id": question.semester.id,
            "name": question.semester.name,
            "code": question.semester.code
        } if question.semester else None,
        "grade": {
            "id": question.grade.id,
            "name": question.grade.name,
            "code": question.grade.code
        } if question.grade else None,
        "subject": {
            "id": question.subject.id,
            "name": question.subject.name,
            "code": question.subject.code
        } if question.subject else None,
        "category": {
            "id": question.category.id,
            "name": question.category.name,
            "code": question.category.code
        } if question.category else None
    }


@router.post("/", summary="创建试题")
async def create_question(
    question_data: QuestionCreate,
    current_admin = Depends(get_current_active_admin)
):
    """创建试题"""
    # 检查权限
    if not current_admin.is_superuser and not await PermissionManager.has_permission(current_admin, PermissionCode.QUESTIONS_CREATE):
        raise HTTPException(status_code=403, detail="Permission denied")
    # 验证关联数据是否存在
    semester = await Semester.filter(id=question_data.semester_id).first()
    if not semester:
        raise HTTPException(status_code=400, detail="Semester not found")

    grade = await Grade.filter(id=question_data.grade_id).first()
    if not grade:
        raise HTTPException(status_code=400, detail="Grade not found")

    subject = await Subject.filter(id=question_data.subject_id).first()
    if not subject:
        raise HTTPException(status_code=400, detail="Subject not found")

    category = await Category.filter(id=question_data.category_id).first()
    if not category:
        raise HTTPException(status_code=400, detail="Category not found")

    # 创建试题时需要使用对象而不是ID
    question_dict = question_data.dict()
    question_dict['semester'] = semester
    question_dict['grade'] = grade
    question_dict['subject'] = subject
    question_dict['category'] = category

    # 移除ID字段，因为我们使用对象
    del question_dict['semester_id']
    del question_dict['grade_id']
    del question_dict['subject_id']
    del question_dict['category_id']

    question = await Question.create(**question_dict)

    # 重新获取完整数据
    question = await Question.filter(id=question.id).prefetch_related(
        "semester", "grade", "subject", "category"
    ).first()

    return {
        "id": question.id,
        "title": question.title,
        "content": question.content,
        "answer": question.answer,
        "difficulty": question.difficulty,
        "question_type": question.question_type,
        "semester_id": question.semester_id,
        "grade_id": question.grade_id,
        "subject_id": question.subject_id,
        "category_id": question.category_id,
        "is_active": question.is_active,
        "is_published": question.is_published,
        "tags": question.tags,
        "source": question.source,
        "author": question.author,
        "view_count": question.view_count,
        "created_at": question.created_at,
        "updated_at": question.updated_at,
        "semester": {
            "id": question.semester.id,
            "name": question.semester.name,
            "code": question.semester.code
        } if question.semester else None,
        "grade": {
            "id": question.grade.id,
            "name": question.grade.name,
            "code": question.grade.code
        } if question.grade else None,
        "subject": {
            "id": question.subject.id,
            "name": question.subject.name,
            "code": question.subject.code
        } if question.subject else None,
        "category": {
            "id": question.category.id,
            "name": question.category.name,
            "code": question.category.code
        } if question.category else None
    }


@router.put("/{question_id}", summary="更新试题")
async def update_question(
    question_id: int,
    question_data: QuestionUpdate,
    current_admin = Depends(get_current_active_admin)
):
    """更新试题"""
    # 检查权限
    if not current_admin.is_superuser and not await PermissionManager.has_permission(current_admin, PermissionCode.QUESTIONS_EDIT):
        raise HTTPException(status_code=403, detail="Permission denied")

    question = await Question.filter(id=question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    update_data = question_data.model_dump(exclude_unset=True)

    # 验证并设置关联数据（如果要更新）
    if question_data.semester_id:
        semester = await Semester.filter(id=question_data.semester_id).first()
        if not semester:
            raise HTTPException(status_code=400, detail="Semester not found")
        update_data['semester'] = semester
        del update_data['semester_id']

    if question_data.grade_id:
        grade = await Grade.filter(id=question_data.grade_id).first()
        if not grade:
            raise HTTPException(status_code=400, detail="Grade not found")
        update_data['grade'] = grade
        del update_data['grade_id']

    if question_data.subject_id:
        subject = await Subject.filter(id=question_data.subject_id).first()
        if not subject:
            raise HTTPException(status_code=400, detail="Subject not found")
        update_data['subject'] = subject
        del update_data['subject_id']

    if question_data.category_id:
        category = await Category.filter(id=question_data.category_id).first()
        if not category:
            raise HTTPException(status_code=400, detail="Category not found")
        update_data['category'] = category
        del update_data['category_id']

    # 更新题目数据
    for field, value in update_data.items():
        setattr(question, field, value)
    await question.save()

    # 重新获取完整数据
    question = await Question.filter(id=question_id).prefetch_related(
        "semester", "grade", "subject", "category"
    ).first()

    return {
        "id": question.id,
        "title": question.title,
        "content": question.content,
        "answer": question.answer,
        "difficulty": question.difficulty,
        "question_type": question.question_type,
        "semester_id": question.semester_id,
        "grade_id": question.grade_id,
        "subject_id": question.subject_id,
        "category_id": question.category_id,
        "is_active": question.is_active,
        "is_published": question.is_published,
        "tags": question.tags,
        "source": question.source,
        "author": question.author,
        "view_count": question.view_count,
        "created_at": question.created_at,
        "updated_at": question.updated_at,
        "semester": {
            "id": question.semester.id,
            "name": question.semester.name,
            "code": question.semester.code
        } if question.semester else None,
        "grade": {
            "id": question.grade.id,
            "name": question.grade.name,
            "code": question.grade.code
        } if question.grade else None,
        "subject": {
            "id": question.subject.id,
            "name": question.subject.name,
            "code": question.subject.code
        } if question.subject else None,
        "category": {
            "id": question.category.id,
            "name": question.category.name,
            "code": question.category.code
        } if question.category else None
    }


@router.delete("/{question_id}", response_model=MessageResponse, summary="删除试题")
async def delete_question(
    question_id: int,
    current_admin = Depends(get_current_active_admin)
):
    """删除试题"""
    # 检查权限
    if not current_admin.is_superuser and not await PermissionManager.has_permission(current_admin, PermissionCode.QUESTIONS_DELETE):
        raise HTTPException(status_code=403, detail="Permission denied")

    question = await Question.filter(id=question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    await question.delete()
    return {"message": "Question deleted successfully"}


# 批量操作相关的Schema
class BatchUpdateRequest(BaseModel):
    question_ids: List[int]
    update_data: dict


class BatchDeleteRequest(BaseModel):
    question_ids: List[int]


class BatchCopyRequest(BaseModel):
    question_ids: List[int]
    target_category_id: Optional[int] = None
    target_subject_id: Optional[int] = None
    target_grade_id: Optional[int] = None
    target_semester_id: Optional[int] = None


@router.post("/batch/update", summary="批量更新试题")
async def batch_update_questions(
    request: BatchUpdateRequest,
    current_admin = Depends(get_current_active_admin)
):
    """批量更新试题"""
    # 检查权限
    if not current_admin.is_superuser and not await PermissionManager.has_permission(current_admin, PermissionCode.QUESTIONS_EDIT):
        raise HTTPException(status_code=403, detail="Permission denied")

    if not request.question_ids:
        raise HTTPException(status_code=400, detail="No question IDs provided")

    # 验证题目是否存在
    questions = await Question.filter(id__in=request.question_ids)
    if len(questions) != len(request.question_ids):
        raise HTTPException(status_code=400, detail="Some questions not found")

    # 验证更新数据中的关联字段
    update_data = request.update_data.copy()

    if 'semester_id' in update_data:
        semester = await Semester.filter(id=update_data['semester_id']).first()
        if not semester:
            raise HTTPException(status_code=400, detail="Semester not found")

    if 'grade_id' in update_data:
        grade = await Grade.filter(id=update_data['grade_id']).first()
        if not grade:
            raise HTTPException(status_code=400, detail="Grade not found")

    if 'subject_id' in update_data:
        subject = await Subject.filter(id=update_data['subject_id']).first()
        if not subject:
            raise HTTPException(status_code=400, detail="Subject not found")

    if 'category_id' in update_data:
        category = await Category.filter(id=update_data['category_id']).first()
        if not category:
            raise HTTPException(status_code=400, detail="Category not found")

    # 执行批量更新
    await Question.filter(id__in=request.question_ids).update(**update_data)

    return {
        "message": f"Successfully updated {len(request.question_ids)} questions",
        "updated_count": len(request.question_ids)
    }


@router.post("/batch/delete", summary="批量删除试题")
async def batch_delete_questions(
    request: BatchDeleteRequest,
    current_admin = Depends(get_current_active_admin)
):
    """批量删除试题"""
    # 检查权限
    if not current_admin.is_superuser and not await PermissionManager.has_permission(current_admin, PermissionCode.QUESTIONS_DELETE):
        raise HTTPException(status_code=403, detail="Permission denied")

    if not request.question_ids:
        raise HTTPException(status_code=400, detail="No question IDs provided")

    # 验证题目是否存在
    questions = await Question.filter(id__in=request.question_ids)
    if len(questions) != len(request.question_ids):
        raise HTTPException(status_code=400, detail="Some questions not found")

    # 执行批量删除
    deleted_count = await Question.filter(id__in=request.question_ids).delete()

    return {
        "message": f"Successfully deleted {deleted_count} questions",
        "deleted_count": deleted_count
    }


@router.post("/batch/copy", summary="批量复制试题")
async def batch_copy_questions(
    request: BatchCopyRequest,
    current_admin = Depends(get_current_active_admin)
):
    """批量复制试题"""
    # 检查权限
    if not current_admin.is_superuser and not await PermissionManager.has_permission(current_admin, PermissionCode.QUESTIONS_CREATE):
        raise HTTPException(status_code=403, detail="Permission denied")

    if not request.question_ids:
        raise HTTPException(status_code=400, detail="No question IDs provided")

    # 获取原始题目
    original_questions = await Question.filter(id__in=request.question_ids).prefetch_related(
        "semester", "grade", "subject", "category"
    )

    if len(original_questions) != len(request.question_ids):
        raise HTTPException(status_code=400, detail="Some questions not found")

    # 验证目标关联数据
    target_semester = None
    target_grade = None
    target_subject = None
    target_category = None

    if request.target_semester_id:
        target_semester = await Semester.filter(id=request.target_semester_id).first()
        if not target_semester:
            raise HTTPException(status_code=400, detail="Target semester not found")

    if request.target_grade_id:
        target_grade = await Grade.filter(id=request.target_grade_id).first()
        if not target_grade:
            raise HTTPException(status_code=400, detail="Target grade not found")

    if request.target_subject_id:
        target_subject = await Subject.filter(id=request.target_subject_id).first()
        if not target_subject:
            raise HTTPException(status_code=400, detail="Target subject not found")

    if request.target_category_id:
        target_category = await Category.filter(id=request.target_category_id).first()
        if not target_category:
            raise HTTPException(status_code=400, detail="Target category not found")

    # 复制题目
    copied_questions = []
    for original in original_questions:
        question_data = {
            "title": f"{original.title} (副本)",
            "content": original.content,
            "answer": original.answer,
            "difficulty": original.difficulty,
            "question_type": original.question_type,
            "semester": target_semester or original.semester,
            "grade": target_grade or original.grade,
            "subject": target_subject or original.subject,
            "category": target_category or original.category,
            "is_active": original.is_active,
            "is_published": False,  # 复制的题目默认未发布
            "tags": original.tags,
            "source": original.source,
            "author": original.author,
            "view_count": 0  # 重置查看次数
        }

        copied_question = await Question.create(**question_data)
        copied_questions.append(copied_question)

    return {
        "message": f"Successfully copied {len(copied_questions)} questions",
        "copied_count": len(copied_questions),
        "copied_question_ids": [q.id for q in copied_questions]
    }

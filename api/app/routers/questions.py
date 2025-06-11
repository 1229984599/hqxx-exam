import random
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
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
    limit: int = Query(20, ge=1, le=100, description="限制数量")
):
    """获取试题列表"""
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

    return result


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
async def get_question(question_id: int):
    """获取试题详情"""
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
    question = await Question.filter(id=question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    update_data = question_data.dict(exclude_unset=True)

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
    question = await Question.filter(id=question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    await question.delete()
    return {"message": "Question deleted successfully"}

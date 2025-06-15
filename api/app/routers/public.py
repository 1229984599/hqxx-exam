"""
公开API路由 - 供前台页面使用，无需认证
"""
import random
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Response
from fastapi.responses import JSONResponse
from app.models.question import Question
from app.models.semester import Semester
from app.models.grade import Grade
from app.models.subject import Subject
from app.models.category import Category
import json
import hashlib

router = APIRouter(prefix="/public", tags=["公开接口"])

# 简单的内存缓存
_cache = {}
_cache_ttl = {}

def get_cache_key(endpoint: str, params: dict) -> str:
    """生成缓存键"""
    cache_data = f"{endpoint}:{json.dumps(params, sort_keys=True)}"
    return hashlib.md5(cache_data.encode()).hexdigest()

def get_from_cache(cache_key: str):
    """从缓存获取数据"""
    import time
    if cache_key in _cache:
        if cache_key in _cache_ttl and time.time() < _cache_ttl[cache_key]:
            return _cache[cache_key]
        else:
            # 缓存过期，清理
            if cache_key in _cache:
                del _cache[cache_key]
            if cache_key in _cache_ttl:
                del _cache_ttl[cache_key]
    return None

def set_cache(cache_key: str, data, ttl_seconds: int = 300):
    """设置缓存数据，默认5分钟过期"""
    import time
    _cache[cache_key] = data
    _cache_ttl[cache_key] = time.time() + ttl_seconds

def add_cache_headers(response: Response, cache_seconds: int = 300):
    """添加缓存头"""
    response.headers["Cache-Control"] = f"public, max-age={cache_seconds}"
    response.headers["ETag"] = f'"{hash(str(response.body))}"'


@router.get("/semesters/", summary="获取学期列表（公开）")
async def get_public_semesters(
    response: Response,
    is_active: bool = Query(True, description="是否激活"),
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(100, ge=1, le=100, description="限制数量")
):
    """获取学期列表 - 公开接口"""
    # 生成缓存键
    cache_key = get_cache_key("semesters", {
        "is_active": is_active,
        "skip": skip,
        "limit": limit
    })

    # 尝试从缓存获取
    cached_data = get_from_cache(cache_key)
    if cached_data:
        add_cache_headers(response, 300)
        return cached_data

    # 查询数据库
    query = Semester.filter(is_active=is_active)
    semesters = await query.offset(skip).limit(limit).order_by("sort_order", "id")

    result = [
        {
            "id": semester.id,
            "name": semester.name,
            "code": semester.code,
            "start_date": semester.start_date,
            "end_date": semester.end_date,
            "is_active": semester.is_active,
            "sort_order": semester.sort_order,
            "description": semester.description
        }
        for semester in semesters
    ]

    # 设置缓存
    set_cache(cache_key, result, 300)  # 5分钟缓存
    add_cache_headers(response, 300)

    return result


@router.get("/grades/", summary="获取年级列表（公开）")
async def get_public_grades(
    response: Response,
    is_active: bool = Query(True, description="是否激活"),
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(100, ge=1, le=100, description="限制数量")
):
    """获取年级列表 - 公开接口"""
    # 生成缓存键
    cache_key = get_cache_key("grades", {
        "is_active": is_active,
        "skip": skip,
        "limit": limit
    })

    # 尝试从缓存获取
    cached_data = get_from_cache(cache_key)
    if cached_data:
        add_cache_headers(response, 300)
        return cached_data

    # 查询数据库
    query = Grade.filter(is_active=is_active)
    grades = await query.offset(skip).limit(limit).order_by("sort_order", "level")

    result = [
        {
            "id": grade.id,
            "name": grade.name,
            "code": grade.code,
            "level": grade.level,
            "is_active": grade.is_active,
            "sort_order": grade.sort_order,
            "description": grade.description
        }
        for grade in grades
    ]

    # 设置缓存
    set_cache(cache_key, result, 300)  # 5分钟缓存
    add_cache_headers(response, 300)

    return result


@router.get("/subjects/", summary="获取学科列表（公开）")
async def get_public_subjects(
    is_active: bool = Query(True, description="是否激活"),
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(100, ge=1, le=100, description="限制数量")
):
    """获取学科列表 - 公开接口"""
    query = Subject.filter(is_active=is_active)
    subjects = await query.offset(skip).limit(limit).order_by("sort_order", "id")
    
    return [
        {
            "id": subject.id,
            "name": subject.name,
            "code": subject.code,
            "is_active": subject.is_active,
            "sort_order": subject.sort_order,
            "description": subject.description
        }
        for subject in subjects
    ]


@router.get("/categories/", summary="获取分类列表（公开）")
async def get_public_categories(
    subject_id: int = Query(None, description="学科ID"),
    is_active: bool = Query(True, description="是否激活"),
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(100, ge=1, le=100, description="限制数量")
):
    """获取分类列表 - 公开接口"""
    query = Category.filter(is_active=is_active)
    
    if subject_id is not None:
        query = query.filter(subject_id=subject_id)
    
    categories = await query.offset(skip).limit(limit).order_by("sort_order", "id")
    
    return [
        {
            "id": category.id,
            "name": category.name,
            "code": category.code,
            "subject_id": category.subject_id,
            "is_active": category.is_active,
            "sort_order": category.sort_order,
            "description": category.description
        }
        for category in categories
    ]


@router.get("/questions/random", summary="随机获取试题（公开）")
async def get_public_random_question(
    semester_id: int = Query(..., description="学期ID"),
    grade_id: int = Query(..., description="年级ID"),
    subject_id: int = Query(..., description="学科ID"),
    category_id: int = Query(..., description="分类ID"),
    difficulty: int = Query(None, ge=1, le=5, description="难度等级"),
    exclude_ids: str = Query(None, description="排除的题目ID列表，逗号分隔")
):
    """随机获取一道试题 - 公开接口"""
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


@router.get("/questions/", summary="获取试题列表（公开）")
async def get_public_questions(
    semester_id: int = Query(None, description="学期ID"),
    grade_id: int = Query(None, description="年级ID"),
    subject_id: int = Query(None, description="学科ID"),
    category_id: int = Query(None, description="分类ID"),
    difficulty: int = Query(None, ge=1, le=5, description="难度等级"),
    question_type: str = Query(None, description="题目类型"),
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(20, ge=1, le=1000, description="限制数量")
):
    """获取试题列表 - 公开接口，只返回已发布的试题"""
    query = Question.filter(
        is_active=True,
        is_published=True
    ).prefetch_related("semester", "grade", "subject", "category")

    if semester_id is not None:
        query = query.filter(semester_id=semester_id)

    if grade_id is not None:
        query = query.filter(grade_id=grade_id)

    if subject_id is not None:
        query = query.filter(subject_id=subject_id)

    if category_id is not None:
        query = query.filter(category_id=category_id)

    if difficulty is not None:
        query = query.filter(difficulty=difficulty)

    if question_type:
        query = query.filter(question_type=question_type)

    questions = await query.offset(skip).limit(limit).order_by("-created_at")

    # 手动序列化
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

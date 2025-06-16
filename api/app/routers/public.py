"""
公开API路由 - 供前台页面使用，无需认证
"""
import random
import logging
from datetime import date
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Response
from fastapi.responses import JSONResponse
from app.models.question import Question
from app.models.semester import Semester
from app.models.grade import Grade
from app.models.subject import Subject
from app.models.category import Category
from app.core.cache import cache_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/public", tags=["公开接口"])

def add_cache_headers(response: Response, cache_seconds: int = 300):
    """添加缓存头"""
    response.headers["Cache-Control"] = f"public, max-age={cache_seconds}"
    response.headers["ETag"] = f'"{hash(str(response.body))}"'


def is_semester_active_by_time(semester) -> bool:
    """检查学期是否在有效时间范围内"""
    if not semester:
        return False

    today = date.today()

    # 如果没有设置开始和结束时间，认为始终有效（向后兼容）
    if not semester.start_date and not semester.end_date:
        return True

    # 如果只设置了开始时间
    if semester.start_date and not semester.end_date:
        return today >= semester.start_date

    # 如果只设置了结束时间
    if not semester.start_date and semester.end_date:
        return today <= semester.end_date

    # 如果都设置了，检查是否在范围内
    return semester.start_date <= today <= semester.end_date


async def validate_semester_time(semester_id: int) -> dict:
    """验证学期时间有效性，返回验证结果和消息"""
    if not semester_id:
        logger.warning(f"学期时间验证失败：未指定学期ID")
        return {"valid": False, "message": "未指定学期"}

    semester = await Semester.filter(id=semester_id, is_active=True).first()
    if not semester:
        logger.warning(f"学期时间验证失败：学期 {semester_id} 不存在或已停用")
        return {"valid": False, "message": "学期不存在或已停用"}

    if not is_semester_active_by_time(semester):
        today = date.today()
        if semester.start_date and today < semester.start_date:
            logger.info(f"学期 {semester_id}({semester.name}) 尚未开始，当前日期：{today}，开始日期：{semester.start_date}")
            return {
                "valid": False,
                "message": f"学期尚未开始，开始时间：{semester.start_date}",
                "code": "SEMESTER_NOT_STARTED"
            }
        elif semester.end_date and today > semester.end_date:
            logger.info(f"学期 {semester_id}({semester.name}) 已结束，当前日期：{today}，结束日期：{semester.end_date}")
            return {
                "valid": False,
                "message": f"学期已结束，结束时间：{semester.end_date}",
                "code": "SEMESTER_ENDED"
            }
        else:
            logger.warning(f"学期 {semester_id}({semester.name}) 时间范围无效，当前日期：{today}")
            return {
                "valid": False,
                "message": "学期不在有效时间范围内",
                "code": "SEMESTER_INVALID_TIME"
            }

    logger.debug(f"学期 {semester_id}({semester.name}) 时间验证通过")
    return {"valid": True, "message": "学期时间有效"}


@router.get("/semesters/", summary="获取学期列表（公开）")
async def get_public_semesters(
    response: Response,
    is_active: bool = Query(True, description="是否激活"),
    only_active_time: bool = Query(False, description="只返回时间范围内的学期"),
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(100, ge=1, le=100, description="限制数量")
):
    """获取学期列表 - 公开接口"""
    # 尝试从缓存获取
    cache_params = {
        "is_active": is_active,
        "only_active_time": only_active_time,
        "skip": skip,
        "limit": limit,
        "date": date.today().isoformat() if only_active_time else None
    }
    cached_data = cache_manager.get("semesters", cache_params)
    if cached_data:
        add_cache_headers(response, 300)
        return cached_data

    # 查询数据库
    query = Semester.filter(is_active=is_active)
    semesters = await query.offset(skip).limit(limit).order_by("sort_order", "id")

    # 如果需要过滤时间范围，则进行过滤
    if only_active_time:
        semesters = [s for s in semesters if is_semester_active_by_time(s)]

    result = [
        {
            "id": semester.id,
            "name": semester.name,
            "code": semester.code,
            "start_date": semester.start_date.isoformat() if semester.start_date else None,
            "end_date": semester.end_date.isoformat() if semester.end_date else None,
            "is_active": semester.is_active,
            "sort_order": semester.sort_order,
            "description": semester.description,
            "is_time_active": is_semester_active_by_time(semester)
        }
        for semester in semesters
    ]

    # 设置缓存
    cache_manager.set("semesters", cache_params, result, 300)  # 5分钟缓存
    add_cache_headers(response, 300)

    return result


@router.get("/semesters/{semester_id}/status", summary="检查学期状态（公开）")
async def check_semester_status(semester_id: int):
    """检查学期状态 - 公开接口"""
    semester_validation = await validate_semester_time(semester_id)

    if semester_validation["valid"]:
        semester = await Semester.filter(id=semester_id, is_active=True).first()
        if not semester:
            return {
                "valid": False,
                "message": "学期不存在或已停用",
                "code": "SEMESTER_NOT_FOUND"
            }

        # 检查是否即将过期（3天内）
        warning_message = None
        if semester.end_date:
            today = date.today()
            days_until_end = (semester.end_date - today).days
            if 0 <= days_until_end <= 3:
                warning_message = f"学期将在 {days_until_end} 天后结束，请抓紧时间完成练习"

        return {
            "valid": True,
            "message": "学期时间有效",
            "semester": {
                "id": semester.id,
                "name": semester.name,
                "code": semester.code,
                "start_date": semester.start_date.isoformat() if semester.start_date else None,
                "end_date": semester.end_date.isoformat() if semester.end_date else None
            },
            "warning": warning_message
        }
    else:
        return semester_validation


@router.get("/grades/", summary="获取年级列表（公开）")
async def get_public_grades(
    response: Response,
    is_active: bool = Query(True, description="是否激活"),
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(100, ge=1, le=100, description="限制数量")
):
    """获取年级列表 - 公开接口"""
    # 尝试从缓存获取
    cache_params = {
        "is_active": is_active,
        "skip": skip,
        "limit": limit
    }
    cached_data = cache_manager.get("grades", cache_params)
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
    cache_manager.set("grades", cache_params, result, 300)  # 5分钟缓存
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

    # 验证学期时间有效性
    semester_validation = await validate_semester_time(semester_id)
    if not semester_validation["valid"]:
        raise HTTPException(
            status_code=400,
            detail={
                "message": semester_validation["message"],
                "code": semester_validation.get("code", "SEMESTER_INVALID"),
                "type": "semester_time_error"
            }
        )

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

    # 如果指定了学期ID，先验证学期时间有效性
    if semester_id is not None:
        semester_validation = await validate_semester_time(semester_id)
        if not semester_validation["valid"]:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": semester_validation["message"],
                    "code": semester_validation.get("code", "SEMESTER_INVALID"),
                    "type": "semester_time_error"
                }
            )

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

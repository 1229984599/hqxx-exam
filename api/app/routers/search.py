from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel
import re
from app.models.question import Question
from app.models.subject import Subject
from app.models.category import Category
from app.models.grade import Grade
from app.models.semester import Semester
from app.dependencies.auth import get_current_active_admin

router = APIRouter(prefix="/search", tags=["搜索功能"])


class SearchResult(BaseModel):
    questions: List[Dict[str, Any]] = []
    subjects: List[Dict[str, Any]] = []
    categories: List[Dict[str, Any]] = []
    grades: List[Dict[str, Any]] = []
    semesters: List[Dict[str, Any]] = []
    total: int = 0


@router.get("/global", response_model=SearchResult, summary="全局搜索")
async def global_search(
    q: str = Query(..., description="搜索关键词", min_length=1),
    limit: int = Query(10, ge=1, le=50, description="每类结果限制数量"),
    type: Optional[str] = Query(None, description="搜索类型过滤"),
    current_admin = Depends(get_current_active_admin)
):
    """
    全局搜索功能
    支持搜索试题、学科、分类、年级、学期
    """
    
    # 清理搜索关键词
    search_query = q.strip()
    if not search_query:
        raise HTTPException(status_code=400, detail="搜索关键词不能为空")
    
    # 构建搜索条件
    search_terms = search_query.split()
    
    result = SearchResult()
    
    # 搜索试题
    if not type or type == "questions":
        questions = await search_questions(search_terms, limit)
        result.questions = questions
    
    # 搜索学科
    if not type or type == "subjects":
        subjects = await search_subjects(search_terms, limit)
        result.subjects = subjects
    
    # 搜索分类
    if not type or type == "categories":
        categories = await search_categories(search_terms, limit)
        result.categories = categories
    
    # 搜索年级
    if not type or type == "grades":
        grades = await search_grades(search_terms, limit)
        result.grades = grades
    
    # 搜索学期
    if not type or type == "semesters":
        semesters = await search_semesters(search_terms, limit)
        result.semesters = semesters
    
    # 计算总数
    result.total = (
        len(result.questions) + 
        len(result.subjects) + 
        len(result.categories) + 
        len(result.grades) + 
        len(result.semesters)
    )
    
    return result


async def search_questions(search_terms: List[str], limit: int) -> List[Dict[str, Any]]:
    """搜索试题"""
    
    # 构建查询条件
    query = Question.filter(is_active=True)
    
    # 多关键词搜索
    for term in search_terms:
        query = query.filter(
            title__icontains=term
        ).union(
            Question.filter(content__icontains=term, is_active=True)
        ).union(
            Question.filter(tags__icontains=term, is_active=True)
        )
    
    # 获取结果并预加载关联数据
    questions = await query.prefetch_related(
        "subject", "grade", "category", "semester"
    ).limit(limit).order_by("-created_at")
    
    # 转换为字典格式
    result = []
    for question in questions:
        result.append({
            "id": question.id,
            "title": question.title,
            "content": question.content[:100] + "..." if len(question.content) > 100 else question.content,
            "difficulty": question.difficulty,
            "question_type": question.question_type,
            "view_count": question.view_count,
            "is_published": question.is_published,
            "created_at": question.created_at.isoformat(),
            "subject": {
                "id": question.subject.id,
                "name": question.subject.name
            } if question.subject else None,
            "grade": {
                "id": question.grade.id,
                "name": question.grade.name
            } if question.grade else None,
            "category": {
                "id": question.category.id,
                "name": question.category.name
            } if question.category else None,
            "semester": {
                "id": question.semester.id,
                "name": question.semester.name
            } if question.semester else None
        })
    
    return result


async def search_subjects(search_terms: List[str], limit: int) -> List[Dict[str, Any]]:
    """搜索学科"""
    
    query = Subject.filter(is_active=True)
    
    for term in search_terms:
        query = query.filter(
            name__icontains=term
        ).union(
            Subject.filter(description__icontains=term, is_active=True)
        ).union(
            Subject.filter(code__icontains=term, is_active=True)
        )
    
    subjects = await query.limit(limit).order_by("sort_order", "name")
    
    result = []
    for subject in subjects:
        # 统计该学科的题目数量
        question_count = await Question.filter(subject_id=subject.id, is_active=True).count()
        
        result.append({
            "id": subject.id,
            "name": subject.name,
            "code": subject.code,
            "description": subject.description,
            "sort_order": subject.sort_order,
            "question_count": question_count,
            "is_active": subject.is_active,
            "created_at": subject.created_at.isoformat()
        })
    
    return result


async def search_categories(search_terms: List[str], limit: int) -> List[Dict[str, Any]]:
    """搜索分类"""
    
    query = Category.filter(is_active=True)
    
    for term in search_terms:
        query = query.filter(
            name__icontains=term
        ).union(
            Category.filter(description__icontains=term, is_active=True)
        ).union(
            Category.filter(code__icontains=term, is_active=True)
        )
    
    categories = await query.prefetch_related("subject").limit(limit).order_by("sort_order", "name")
    
    result = []
    for category in categories:
        # 统计该分类的题目数量
        question_count = await Question.filter(category_id=category.id, is_active=True).count()
        
        result.append({
            "id": category.id,
            "name": category.name,
            "code": category.code,
            "description": category.description,
            "sort_order": category.sort_order,
            "question_count": question_count,
            "is_active": category.is_active,
            "created_at": category.created_at.isoformat(),
            "subject": {
                "id": category.subject.id,
                "name": category.subject.name
            } if category.subject else None
        })
    
    return result


async def search_grades(search_terms: List[str], limit: int) -> List[Dict[str, Any]]:
    """搜索年级"""
    
    query = Grade.filter(is_active=True)
    
    for term in search_terms:
        query = query.filter(
            name__icontains=term
        ).union(
            Grade.filter(description__icontains=term, is_active=True)
        )
    
    grades = await query.limit(limit).order_by("sort_order", "name")
    
    result = []
    for grade in grades:
        # 统计该年级的题目数量
        question_count = await Question.filter(grade_id=grade.id, is_active=True).count()
        
        result.append({
            "id": grade.id,
            "name": grade.name,
            "description": grade.description,
            "sort_order": grade.sort_order,
            "question_count": question_count,
            "is_active": grade.is_active,
            "created_at": grade.created_at.isoformat()
        })
    
    return result


async def search_semesters(search_terms: List[str], limit: int) -> List[Dict[str, Any]]:
    """搜索学期"""
    
    query = Semester.filter(is_active=True)
    
    for term in search_terms:
        query = query.filter(
            name__icontains=term
        ).union(
            Semester.filter(description__icontains=term, is_active=True)
        )
    
    semesters = await query.limit(limit).order_by("-start_date", "name")
    
    result = []
    for semester in semesters:
        # 统计该学期的题目数量
        question_count = await Question.filter(semester_id=semester.id, is_active=True).count()
        
        result.append({
            "id": semester.id,
            "name": semester.name,
            "description": semester.description,
            "start_date": semester.start_date.isoformat() if semester.start_date else None,
            "end_date": semester.end_date.isoformat() if semester.end_date else None,
            "question_count": question_count,
            "is_active": semester.is_active,
            "created_at": semester.created_at.isoformat()
        })
    
    return result


@router.get("/suggestions", summary="搜索建议")
async def get_search_suggestions(
    q: str = Query(..., description="搜索关键词前缀", min_length=1),
    limit: int = Query(5, ge=1, le=20, description="建议数量"),
    current_admin = Depends(get_current_active_admin)
):
    """
    获取搜索建议
    基于已有数据提供搜索建议
    """
    
    search_prefix = q.strip()
    if not search_prefix:
        return {"suggestions": []}
    
    suggestions = []
    
    # 从试题标题获取建议
    questions = await Question.filter(
        title__icontains=search_prefix,
        is_active=True
    ).limit(limit).values("title")
    
    for question in questions:
        if question["title"] not in suggestions:
            suggestions.append(question["title"])
    
    # 从学科名称获取建议
    subjects = await Subject.filter(
        name__icontains=search_prefix,
        is_active=True
    ).limit(limit).values("name")
    
    for subject in subjects:
        if subject["name"] not in suggestions and len(suggestions) < limit:
            suggestions.append(subject["name"])
    
    # 从分类名称获取建议
    categories = await Category.filter(
        name__icontains=search_prefix,
        is_active=True
    ).limit(limit).values("name")
    
    for category in categories:
        if category["name"] not in suggestions and len(suggestions) < limit:
            suggestions.append(category["name"])
    
    return {
        "suggestions": suggestions[:limit]
    }


@router.get("/popular", summary="热门搜索")
async def get_popular_searches(
    limit: int = Query(10, ge=1, le=20, description="返回数量"),
    current_admin = Depends(get_current_active_admin)
):
    """
    获取热门搜索关键词
    基于题目查看次数等数据
    """
    
    # 获取查看次数最多的题目标题关键词
    popular_questions = await Question.filter(
        is_active=True,
        view_count__gt=0
    ).order_by("-view_count").limit(limit).values("title", "view_count")
    
    # 提取关键词
    keywords = []
    for question in popular_questions:
        title = question["title"]
        # 简单的关键词提取（可以后续优化）
        words = re.findall(r'[\u4e00-\u9fff]+', title)  # 提取中文词汇
        for word in words:
            if len(word) >= 2 and word not in keywords:
                keywords.append(word)
    
    # 获取热门学科
    subjects = await Subject.filter(is_active=True).order_by("sort_order").limit(5).values("name")
    for subject in subjects:
        if subject["name"] not in keywords:
            keywords.append(subject["name"])
    
    return {
        "popular_keywords": keywords[:limit]
    }

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, Query
from datetime import datetime, timedelta
from tortoise.functions import Count, Sum, Avg
from app.models.question import Question
from app.models.semester import Semester
from app.models.grade import Grade
from app.models.subject import Subject
from app.models.category import Category
from app.models.admin import Admin
from app.dependencies.auth import get_current_active_admin

router = APIRouter(prefix="/analytics", tags=["数据分析"])


@router.get("/dashboard", summary="获取仪表板统计数据")
async def get_dashboard_stats():
    """获取仪表板统计数据"""
    
    # 基础统计
    total_questions = await Question.all().count()
    total_semesters = await Semester.all().count()
    total_grades = await Grade.all().count()
    total_subjects = await Subject.all().count()
    total_categories = await Category.all().count()
    total_admins = await Admin.all().count()
    
    # 活跃数据统计
    active_questions = await Question.filter(is_active=True).count()
    published_questions = await Question.filter(is_published=True).count()
    active_semesters = await Semester.filter(is_active=True).count()
    active_subjects = await Subject.filter(is_active=True).count()
    
    # 最近7天新增数据
    seven_days_ago = datetime.now() - timedelta(days=7)
    recent_questions = await Question.filter(created_at__gte=seven_days_ago).count()
    
    # 题目难度分布
    difficulty_stats = []
    for i in range(1, 6):
        count = await Question.filter(difficulty=i).count()
        difficulty_stats.append({
            "difficulty": i,
            "count": count,
            "percentage": round((count / total_questions * 100) if total_questions > 0 else 0, 1)
        })
    
    # 学科题目分布
    subject_stats = []
    subjects = await Subject.all()
    for subject in subjects:
        question_count = await Question.filter(subject_id=subject.id).count()
        subject_stats.append({
            "subject_id": subject.id,
            "subject_name": subject.name,
            "question_count": question_count,
            "percentage": round((question_count / total_questions * 100) if total_questions > 0 else 0, 1)
        })
    
    # 年级题目分布
    grade_stats = []
    grades = await Grade.all()
    for grade in grades:
        question_count = await Question.filter(grade_id=grade.id).count()
        grade_stats.append({
            "grade_id": grade.id,
            "grade_name": grade.name,
            "question_count": question_count,
            "percentage": round((question_count / total_questions * 100) if total_questions > 0 else 0, 1)
        })
    
    return {
        "basic_stats": {
            "total_questions": total_questions,
            "total_semesters": total_semesters,
            "total_grades": total_grades,
            "total_subjects": total_subjects,
            "total_categories": total_categories,
            "total_admins": total_admins,
            "active_questions": active_questions,
            "published_questions": published_questions,
            "active_semesters": active_semesters,
            "active_subjects": active_subjects,
            "recent_questions": recent_questions
        },
        "difficulty_distribution": difficulty_stats,
        "subject_distribution": subject_stats,
        "grade_distribution": grade_stats
    }


@router.get("/questions/trends", summary="获取题目趋势数据")
async def get_question_trends(
    days: int = Query(30, ge=7, le=365, description="统计天数")
):
    """获取题目创建趋势数据"""
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # 按天统计题目创建数量
    daily_stats = []
    current_date = start_date
    
    while current_date <= end_date:
        next_date = current_date + timedelta(days=1)
        count = await Question.filter(
            created_at__gte=current_date,
            created_at__lt=next_date
        ).count()
        
        daily_stats.append({
            "date": current_date.strftime("%Y-%m-%d"),
            "count": count
        })
        
        current_date = next_date
    
    return {
        "period": f"{days}天",
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "daily_stats": daily_stats
    }


@router.get("/questions/popular", summary="获取热门题目统计")
async def get_popular_questions(
    limit: int = Query(10, ge=5, le=50, description="返回数量")
):
    """获取最受欢迎的题目"""
    
    # 按查看次数排序
    popular_questions = await Question.filter(is_active=True).prefetch_related(
        "subject", "grade", "category"
    ).order_by("-view_count").limit(limit)
    
    result = []
    for question in popular_questions:
        result.append({
            "id": question.id,
            "title": question.title,
            "view_count": question.view_count,
            "difficulty": question.difficulty,
            "subject_name": question.subject.name,
            "grade_name": question.grade.name,
            "category_name": question.category.name,
            "created_at": question.created_at.strftime("%Y-%m-%d")
        })
    
    return {
        "popular_questions": result
    }


@router.get("/categories/stats", summary="获取分类统计数据")
async def get_category_stats():
    """获取分类统计数据"""
    
    categories = await Category.all().prefetch_related("subject")
    category_stats = []
    
    for category in categories:
        question_count = await Question.filter(category_id=category.id).count()
        active_question_count = await Question.filter(
            category_id=category.id, 
            is_active=True
        ).count()
        
        # 计算平均难度
        questions = await Question.filter(category_id=category.id)
        avg_difficulty = sum(q.difficulty for q in questions) / len(questions) if questions else 0
        
        category_stats.append({
            "category_id": category.id,
            "category_name": category.name,
            "category_code": category.code,
            "subject_name": category.subject.name if category.subject else "未分配",
            "question_count": question_count,
            "active_question_count": active_question_count,
            "avg_difficulty": round(avg_difficulty, 1),
            "is_active": category.is_active
        })
    
    # 按题目数量排序
    category_stats.sort(key=lambda x: x["question_count"], reverse=True)
    
    return {
        "category_stats": category_stats
    }


@router.get("/usage/summary", summary="获取使用情况汇总")
async def get_usage_summary():
    """获取系统使用情况汇总"""
    
    # 总体使用统计
    total_views = await Question.all().values_list("view_count", flat=True)
    total_view_count = sum(total_views) if total_views else 0
    
    # 最活跃的学科
    subject_usage = []
    subjects = await Subject.all()
    for subject in subjects:
        questions = await Question.filter(subject_id=subject.id)
        subject_views = sum(q.view_count for q in questions)
        question_count = len(questions)
        
        subject_usage.append({
            "subject_name": subject.name,
            "question_count": question_count,
            "total_views": subject_views,
            "avg_views_per_question": round(subject_views / question_count, 1) if question_count > 0 else 0
        })
    
    subject_usage.sort(key=lambda x: x["total_views"], reverse=True)
    
    # 最活跃的年级
    grade_usage = []
    grades = await Grade.all()
    for grade in grades:
        questions = await Question.filter(grade_id=grade.id)
        grade_views = sum(q.view_count for q in questions)
        question_count = len(questions)
        
        grade_usage.append({
            "grade_name": grade.name,
            "question_count": question_count,
            "total_views": grade_views,
            "avg_views_per_question": round(grade_views / question_count, 1) if question_count > 0 else 0
        })
    
    grade_usage.sort(key=lambda x: x["total_views"], reverse=True)
    
    return {
        "total_view_count": total_view_count,
        "subject_usage": subject_usage[:10],  # 前10名
        "grade_usage": grade_usage[:10]       # 前10名
    }


@router.get("/performance", summary="获取系统性能统计")
async def get_performance_stats():
    """获取系统性能相关统计"""
    
    # 数据库大小估算（基于记录数）
    db_stats = {
        "questions": await Question.all().count(),
        "semesters": await Semester.all().count(),
        "grades": await Grade.all().count(),
        "subjects": await Subject.all().count(),
        "categories": await Category.all().count(),
        "admins": await Admin.all().count()
    }
    
    # 数据质量统计
    questions_without_answer = await Question.filter(answer__isnull=True).count()
    questions_without_tags = await Question.filter(tags__isnull=True).count()
    inactive_questions = await Question.filter(is_active=False).count()
    unpublished_questions = await Question.filter(is_published=False).count()
    
    quality_stats = {
        "questions_without_answer": questions_without_answer,
        "questions_without_tags": questions_without_tags,
        "inactive_questions": inactive_questions,
        "unpublished_questions": unpublished_questions,
        "total_questions": await Question.all().count()
    }
    
    return {
        "database_stats": db_stats,
        "data_quality": quality_stats
    }

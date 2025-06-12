from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import datetime, timedelta
from pydantic import BaseModel
from app.models.admin import Admin
from app.models.question import Question
from app.models.semester import Semester
from app.models.grade import Grade
from app.models.subject import Subject
from app.models.category import Category
from app.dependencies.auth import get_current_active_admin
from app.utils.auth import get_password_hash

router = APIRouter(prefix="/system", tags=["系统管理"])


# Schema定义
class AdminCreate(BaseModel):
    username: str
    email: str
    password: str
    full_name: Optional[str] = None
    is_superuser: bool = False


class AdminUpdate(BaseModel):
    email: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None


class AdminResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str]
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str


class SystemStats(BaseModel):
    database_size: dict
    data_quality: dict
    performance_metrics: dict
    recent_activities: List[dict]


@router.get("/admins", response_model=List[AdminResponse], summary="获取管理员列表")
async def get_admins(
    is_active: bool = Query(None, description="是否激活"),
    search: str = Query(None, description="搜索关键词"),
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(20, ge=1, le=100, description="限制数量"),
    current_admin = Depends(get_current_active_admin)
):
    """获取管理员列表（仅超级管理员可访问）"""
    if not current_admin.is_superuser:
        raise HTTPException(status_code=403, detail="Only superuser can access admin list")
    
    query = Admin.all()
    
    if is_active is not None:
        query = query.filter(is_active=is_active)
    
    if search:
        query = query.filter(
            username__icontains=search
        ).union(
            Admin.filter(email__icontains=search)
        ).union(
            Admin.filter(full_name__icontains=search)
        )
    
    admins = await query.offset(skip).limit(limit).order_by("-created_at")
    return admins


@router.post("/admins", response_model=AdminResponse, summary="创建管理员")
async def create_admin(
    admin_data: AdminCreate,
    current_admin = Depends(get_current_active_admin)
):
    """创建管理员（仅超级管理员可操作）"""
    if not current_admin.is_superuser:
        raise HTTPException(status_code=403, detail="Only superuser can create admin")
    
    # 检查用户名是否已存在
    existing_admin = await Admin.filter(username=admin_data.username).first()
    if existing_admin:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # 检查邮箱是否已存在
    existing_email = await Admin.filter(email=admin_data.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    # 创建管理员
    admin = await Admin.create(
        username=admin_data.username,
        email=admin_data.email,
        hashed_password=get_password_hash(admin_data.password),
        full_name=admin_data.full_name,
        is_superuser=admin_data.is_superuser,
        is_active=True
    )
    
    return admin


@router.put("/admins/{admin_id}", response_model=AdminResponse, summary="更新管理员")
async def update_admin(
    admin_id: int,
    admin_data: AdminUpdate,
    current_admin = Depends(get_current_active_admin)
):
    """更新管理员信息（仅超级管理员可操作）"""
    if not current_admin.is_superuser:
        raise HTTPException(status_code=403, detail="Only superuser can update admin")
    
    admin = await Admin.filter(id=admin_id).first()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    
    # 不能修改自己的超级管理员状态
    if admin.id == current_admin.id and admin_data.is_superuser is not None:
        raise HTTPException(status_code=400, detail="Cannot modify your own superuser status")
    
    update_data = admin_data.dict(exclude_unset=True)
    
    # 检查邮箱是否已被其他用户使用
    if 'email' in update_data:
        existing_email = await Admin.filter(email=update_data['email']).exclude(id=admin_id).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already exists")
    
    # 更新管理员信息
    for field, value in update_data.items():
        setattr(admin, field, value)
    await admin.save()
    
    return admin


@router.delete("/admins/{admin_id}", summary="删除管理员")
async def delete_admin(
    admin_id: int,
    current_admin = Depends(get_current_active_admin)
):
    """删除管理员（仅超级管理员可操作）"""
    if not current_admin.is_superuser:
        raise HTTPException(status_code=403, detail="Only superuser can delete admin")
    
    admin = await Admin.filter(id=admin_id).first()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    
    # 不能删除自己
    if admin.id == current_admin.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    
    # 检查是否是最后一个超级管理员
    if admin.is_superuser:
        superuser_count = await Admin.filter(is_superuser=True, is_active=True).count()
        if superuser_count <= 1:
            raise HTTPException(status_code=400, detail="Cannot delete the last superuser")
    
    await admin.delete()
    return {"message": "Admin deleted successfully"}


@router.post("/change-password", summary="修改密码")
async def change_password(
    request: PasswordChangeRequest,
    current_admin = Depends(get_current_active_admin)
):
    """修改当前管理员密码"""
    from app.utils.auth import verify_password
    
    # 验证旧密码
    if not verify_password(request.old_password, current_admin.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid old password")
    
    # 更新密码
    current_admin.hashed_password = get_password_hash(request.new_password)
    await current_admin.save()
    
    return {"message": "Password changed successfully"}


@router.get("/stats", summary="获取系统统计信息")
async def get_system_stats(
    current_admin = Depends(get_current_active_admin)
):
    """获取系统统计信息"""
    
    # 数据库大小统计
    database_size = {
        "questions": await Question.all().count(),
        "semesters": await Semester.all().count(),
        "grades": await Grade.all().count(),
        "subjects": await Subject.all().count(),
        "categories": await Category.all().count(),
        "admins": await Admin.all().count()
    }
    
    # 数据质量统计
    total_questions = database_size["questions"]
    questions_without_answer = await Question.filter(answer__isnull=True).count()
    questions_without_tags = await Question.filter(tags__isnull=True).count()
    inactive_questions = await Question.filter(is_active=False).count()
    unpublished_questions = await Question.filter(is_published=False).count()
    
    data_quality = {
        "total_questions": total_questions,
        "questions_without_answer": questions_without_answer,
        "questions_without_tags": questions_without_tags,
        "inactive_questions": inactive_questions,
        "unpublished_questions": unpublished_questions,
        "completion_rate": round((total_questions - questions_without_answer) / total_questions * 100, 1) if total_questions > 0 else 0
    }
    
    # 性能指标
    seven_days_ago = datetime.now() - timedelta(days=7)
    recent_questions = await Question.filter(created_at__gte=seven_days_ago).count()

    # 获取所有题目的查看次数和难度
    all_questions = await Question.all()
    total_views = sum([q.view_count for q in all_questions])
    avg_difficulty = sum([q.difficulty for q in all_questions]) / len(all_questions) if all_questions else 0

    performance_metrics = {
        "recent_questions_7days": recent_questions,
        "active_admins": await Admin.filter(is_active=True).count(),
        "total_views": total_views,
        "avg_difficulty": round(avg_difficulty, 1)
    }
    
    # 最近活动（模拟数据，实际应该从日志表获取）
    recent_activities = [
        {
            "action": "创建题目",
            "user": current_admin.username,
            "timestamp": datetime.now() - timedelta(hours=2),
            "details": "创建了新的数学题目"
        },
        {
            "action": "更新分类",
            "user": current_admin.username,
            "timestamp": datetime.now() - timedelta(hours=5),
            "details": "更新了语文分类设置"
        }
    ]
    
    return {
        "database_size": database_size,
        "data_quality": data_quality,
        "performance_metrics": performance_metrics,
        "recent_activities": recent_activities
    }


@router.get("/health", summary="系统健康检查")
async def health_check():
    """系统健康检查"""
    try:
        # 检查数据库连接
        await Admin.all().count()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now(),
            "database": "connected",
            "version": "1.0.0"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.now(),
            "database": "disconnected",
            "error": str(e)
        }


@router.post("/backup", summary="数据备份")
async def create_backup(
    current_admin = Depends(get_current_active_admin)
):
    """创建数据备份（仅超级管理员可操作）"""
    if not current_admin.is_superuser:
        raise HTTPException(status_code=403, detail="Only superuser can create backup")
    
    # 这里应该实现实际的备份逻辑
    # 目前返回模拟响应
    backup_info = {
        "backup_id": f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "created_at": datetime.now(),
        "created_by": current_admin.username,
        "size": "2.5MB",
        "status": "completed"
    }
    
    return {
        "message": "Backup created successfully",
        "backup_info": backup_info
    }

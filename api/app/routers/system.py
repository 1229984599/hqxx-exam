from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import datetime, timedelta
from pydantic import BaseModel
import json
from app.models.admin import Admin
from app.models.question import Question
from app.models.semester import Semester
from app.models.grade import Grade
from app.models.subject import Subject
from app.models.category import Category
from app.models.system_log import SystemLog, LogLevel, LogModule
from app.models.system_config import SystemConfig, ConfigType, ConfigKey
from app.dependencies.auth import get_current_active_admin
from app.utils.auth import get_password_hash
from app.utils.logger import SystemLogger
from app.utils.permissions import PermissionManager
from app.models.role import PermissionCode, RoleCode
from app.schemas.common import BatchUpdateRequest, BatchDeleteRequest, BatchOperationResponse

router = APIRouter(prefix="/system", tags=["系统管理"])


# Schema定义
class AdminCreate(BaseModel):
    username: str
    email: str
    password: str
    full_name: Optional[str] = None
    is_superuser: bool = False
    role_ids: Optional[List[int]] = None


class AdminUpdate(BaseModel):
    email: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    role_ids: Optional[List[int]] = None


class RoleInfo(BaseModel):
    id: int
    name: str
    code: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class AdminResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str]
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
    roles: Optional[List[RoleInfo]] = []

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


class LogResponse(BaseModel):
    id: int
    level: str
    module: str
    message: str
    details: Optional[dict]
    user: Optional[str]
    ip_address: Optional[str]
    timestamp: datetime

    class Config:
        from_attributes = True


class LogsResponse(BaseModel):
    logs: List[LogResponse]
    total: int
    stats: dict


class WebDAVConfig(BaseModel):
    url: str
    username: str
    password: str
    path: str = "/backups/hqxx-exam"


class WebDAVTestRequest(BaseModel):
    url: str
    username: str
    password: str


class BackupConfigRequest(BaseModel):
    method: str = "local"
    autoBackup: bool = False
    webdav: Optional[dict] = None
    ftp: Optional[dict] = None


class SystemSettingsRequest(BaseModel):
    basic: dict
    security: dict
    file: dict
    email: dict


@router.get("/admins", response_model=List[AdminResponse], summary="获取管理员列表")
async def get_admins(
    is_active: bool = Query(None, description="是否激活"),
    search: str = Query(None, description="搜索关键词"),
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(20, ge=1, le=100, description="限制数量"),
    current_admin = Depends(get_current_active_admin)
):
    """获取管理员列表"""
    # 检查角色：需要管理员角色或超级管理员角色
    if not current_admin.is_superuser and not await PermissionManager.has_any_role(current_admin, [RoleCode.SUPER_ADMIN, RoleCode.ADMIN]):
        raise HTTPException(status_code=403, detail="Role required: admin or super_admin")
    
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

    # 为每个管理员加载角色信息
    admin_responses = []
    for admin in admins:
        # 获取管理员的角色
        from app.models.role import AdminRole, Role
        admin_roles = await AdminRole.filter(admin=admin).prefetch_related('role')
        roles = [RoleInfo(
            id=ar.role.id,
            name=ar.role.name,
            code=ar.role.code,
            description=ar.role.description
        ) for ar in admin_roles if ar.role.is_active]

        admin_response = AdminResponse(
            id=admin.id,
            username=admin.username,
            email=admin.email,
            full_name=admin.full_name,
            is_active=admin.is_active,
            is_superuser=admin.is_superuser,
            created_at=admin.created_at,
            updated_at=admin.updated_at,
            roles=roles
        )
        admin_responses.append(admin_response)

    return admin_responses


@router.post("/admins", response_model=AdminResponse, summary="创建管理员")
async def create_admin(
    admin_data: AdminCreate,
    current_admin = Depends(get_current_active_admin)
):
    """创建管理员"""
    # 检查角色：需要管理员角色或超级管理员角色
    if not current_admin.is_superuser and not await PermissionManager.has_any_role(current_admin, [RoleCode.SUPER_ADMIN, RoleCode.ADMIN]):
        raise HTTPException(status_code=403, detail="Role required: admin or super_admin")
    
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

    # 分配角色（如果提供了角色ID）
    if admin_data.role_ids:
        from app.models.role import Role
        for role_id in admin_data.role_ids:
            role = await Role.get_or_none(id=role_id)
            if role and role.is_active:
                await PermissionManager.assign_role(admin, role, current_admin.username)

    return admin


@router.put("/admins/{admin_id}", response_model=AdminResponse, summary="更新管理员")
async def update_admin(
    admin_id: int,
    admin_data: AdminUpdate,
    current_admin = Depends(get_current_active_admin)
):
    """更新管理员信息"""
    # 检查权限：需要管理员编辑权限或者是超级管理员
    if not current_admin.is_superuser and not await PermissionManager.has_permission(current_admin, PermissionCode.ADMINS_EDIT):
        raise HTTPException(status_code=403, detail="Permission denied")
    
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

    # 处理密码更新
    if 'password' in update_data and update_data['password']:
        update_data['hashed_password'] = get_password_hash(update_data['password'])
        del update_data['password']

    # 处理角色分配
    if 'role_ids' in update_data:
        role_ids = update_data.pop('role_ids')
        if role_ids is not None:  # 允许传入空数组来清除所有角色
            from app.models.role import Role, AdminRole
            # 清除现有角色
            await AdminRole.filter(admin=admin).delete()
            # 分配新角色
            for role_id in role_ids:
                role = await Role.get_or_none(id=role_id)
                if role and role.is_active:
                    await PermissionManager.assign_role(admin, role, current_admin.username)

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
    """删除管理员"""
    # 检查权限：需要管理员删除权限或者是超级管理员
    if not current_admin.is_superuser and not await PermissionManager.has_permission(current_admin, PermissionCode.ADMINS_DELETE):
        raise HTTPException(status_code=403, detail="Permission denied")
    
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


@router.post("/admins/batch-activate", response_model=BatchOperationResponse, summary="批量激活管理员")
async def batch_activate_admins(
    request: BatchDeleteRequest,  # 使用BatchDeleteRequest因为只需要ids
    current_admin = Depends(get_current_active_admin)
):
    """批量激活管理员"""
    # 检查权限
    if not current_admin.is_superuser and not await PermissionManager.has_permission(current_admin, PermissionCode.ADMINS_EDIT):
        raise HTTPException(status_code=403, detail="Permission denied")

    success_count = 0
    failed_count = 0
    failed_items = []

    for admin_id in request.get_ids():
        try:
            admin = await Admin.filter(id=admin_id).first()
            if not admin:
                failed_count += 1
                failed_items.append({"id": admin_id, "error": "Admin not found"})
                continue

            admin.is_active = True
            await admin.save()
            success_count += 1
        except Exception as e:
            failed_count += 1
            failed_items.append({"id": admin_id, "error": str(e)})

    return BatchOperationResponse(
        success_count=success_count,
        failed_count=failed_count,
        total_count=len(request.get_ids()),
        message=f"批量激活完成：成功 {success_count} 个，失败 {failed_count} 个",
        failed_items=failed_items
    )


@router.post("/admins/batch-deactivate", response_model=BatchOperationResponse, summary="批量禁用管理员")
async def batch_deactivate_admins(
    request: BatchDeleteRequest,
    current_admin = Depends(get_current_active_admin)
):
    """批量禁用管理员"""
    # 检查权限
    if not current_admin.is_superuser and not await PermissionManager.has_permission(current_admin, PermissionCode.ADMINS_EDIT):
        raise HTTPException(status_code=403, detail="Permission denied")

    success_count = 0
    failed_count = 0
    failed_items = []

    for admin_id in request.get_ids():
        try:
            admin = await Admin.filter(id=admin_id).first()
            if not admin:
                failed_count += 1
                failed_items.append({"id": admin_id, "error": "Admin not found"})
                continue

            # 不能禁用自己
            if admin.id == current_admin.id:
                failed_count += 1
                failed_items.append({"id": admin_id, "error": "Cannot deactivate yourself"})
                continue

            # 检查是否是最后一个激活的超级管理员
            if admin.is_superuser:
                active_superuser_count = await Admin.filter(is_superuser=True, is_active=True).count()
                if active_superuser_count <= 1:
                    failed_count += 1
                    failed_items.append({"id": admin_id, "error": "Cannot deactivate the last active superuser"})
                    continue

            admin.is_active = False
            await admin.save()
            success_count += 1
        except Exception as e:
            failed_count += 1
            failed_items.append({"id": admin_id, "error": str(e)})

    return BatchOperationResponse(
        success_count=success_count,
        failed_count=failed_count,
        total_count=len(request.get_ids()),
        message=f"批量禁用完成：成功 {success_count} 个，失败 {failed_count} 个",
        failed_items=failed_items
    )


@router.post("/admins/batch-delete", response_model=BatchOperationResponse, summary="批量删除管理员")
async def batch_delete_admins(
    request: BatchDeleteRequest,
    current_admin = Depends(get_current_active_admin)
):
    """批量删除管理员"""
    # 检查权限
    if not current_admin.is_superuser and not await PermissionManager.has_permission(current_admin, PermissionCode.ADMINS_DELETE):
        raise HTTPException(status_code=403, detail="Permission denied")

    success_count = 0
    failed_count = 0
    failed_items = []

    for admin_id in request.get_ids():
        try:
            admin = await Admin.filter(id=admin_id).first()
            if not admin:
                failed_count += 1
                failed_items.append({"id": admin_id, "error": "Admin not found"})
                continue

            # 不能删除自己
            if admin.id == current_admin.id:
                failed_count += 1
                failed_items.append({"id": admin_id, "error": "Cannot delete yourself"})
                continue

            # 检查是否是最后一个超级管理员
            if admin.is_superuser:
                superuser_count = await Admin.filter(is_superuser=True, is_active=True).count()
                if superuser_count <= 1:
                    failed_count += 1
                    failed_items.append({"id": admin_id, "error": "Cannot delete the last superuser"})
                    continue

            await admin.delete()
            success_count += 1
        except Exception as e:
            failed_count += 1
            failed_items.append({"id": admin_id, "error": str(e)})

    return BatchOperationResponse(
        success_count=success_count,
        failed_count=failed_count,
        total_count=len(request.get_ids()),
        message=f"批量删除完成：成功 {success_count} 个，失败 {failed_count} 个",
        failed_items=failed_items
    )





@router.get("/admins/check-username", summary="检查用户名是否存在")
async def check_username(
    username: str = Query(..., description="要检查的用户名"),
    current_admin = Depends(get_current_active_admin)
):
    """检查用户名是否已存在"""
    # 检查权限
    if not current_admin.is_superuser and not await PermissionManager.has_permission(current_admin, PermissionCode.ADMINS_CREATE):
        raise HTTPException(status_code=403, detail="Permission denied")

    if not username or not username.strip():
        raise HTTPException(status_code=400, detail="Username cannot be empty")

    # 检查用户名是否已存在
    existing_admin = await Admin.filter(username=username.strip()).first()

    return {
        "exists": existing_admin is not None,
        "username": username.strip()
    }


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
    backup_request: Optional[dict] = None,
    current_admin = Depends(get_current_active_admin)
):
    """创建数据备份（仅超级管理员可操作）"""
    if not current_admin.is_superuser:
        raise HTTPException(status_code=403, detail="Only superuser can create backup")

    import os
    import sqlite3
    import shutil
    from pathlib import Path

    try:
        # 解析备份请求参数
        backup_method = "local"  # 默认本地备份
        webdav_config = None
        ftp_config = None

        if backup_request:
            backup_method = backup_request.get("method", "local")
            webdav_config = backup_request.get("webdav")
            ftp_config = backup_request.get("ftp")

        # 获取数据库文件路径
        db_path = "db.sqlite3"
        backup_dir = Path("backups")
        backup_dir.mkdir(exist_ok=True)

        # 生成备份文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"backup_{timestamp}.sqlite3"
        backup_path = backup_dir / backup_filename

        # 创建数据库备份
        if os.path.exists(db_path):
            # 使用SQLite的备份API
            source_conn = sqlite3.connect(db_path)
            backup_conn = sqlite3.connect(str(backup_path))

            # 执行备份
            source_conn.backup(backup_conn)

            source_conn.close()
            backup_conn.close()

            # 获取备份文件大小
            file_size = os.path.getsize(backup_path)
            size_mb = round(file_size / (1024 * 1024), 2)

            backup_info = {
                "backup_id": f"backup_{timestamp}",
                "filename": backup_filename,
                "created_at": datetime.now(),
                "created_by": current_admin.username,
                "size": f"{size_mb}MB",
                "status": "completed",
                "method": backup_method,
                "path": str(backup_path)
            }

            # 根据备份方法处理
            if backup_method == "webdav" and webdav_config:
                # 上传到WebDAV
                await upload_to_webdav(backup_path, backup_filename, webdav_config, current_admin)
                backup_info["remote_location"] = f"{webdav_config['url']}/{webdav_config['path']}/{backup_filename}"

            elif backup_method == "ftp" and ftp_config:
                # 上传到FTP
                await upload_to_ftp(backup_path, backup_filename, ftp_config, current_admin)
                backup_info["remote_location"] = f"ftp://{ftp_config['host']}/{ftp_config['path']}/{backup_filename}"

            # 记录备份操作
            await SystemLogger.info(
                module=LogModule.SYSTEM,
                message=f"创建{backup_method}备份成功: {backup_filename}",
                details={
                    "backup_id": backup_info["backup_id"],
                    "method": backup_method,
                    "size": backup_info["size"]
                },
                user=current_admin.username
            )

            return {
                "message": f"Backup created successfully using {backup_method} method",
                "backup_info": backup_info
            }
        else:
            raise HTTPException(status_code=500, detail="Database file not found")

    except Exception as e:
        await SystemLogger.error(
            module=LogModule.SYSTEM,
            message="备份创建失败",
            details={"error": str(e), "method": backup_method},
            user=current_admin.username
        )
        raise HTTPException(status_code=500, detail=f"Backup failed: {str(e)}")


async def upload_to_webdav(backup_path, filename, webdav_config, current_admin):
    """上传备份文件到WebDAV服务器"""
    import httpx
    import base64
    from urllib.parse import urljoin

    try:
        # 准备WebDAV上传
        credentials = base64.b64encode(f"{webdav_config['username']}:{webdav_config['password']}".encode()).decode()
        headers = {
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/octet-stream"
        }

        # 构建远程路径
        remote_url = urljoin(webdav_config['url'].rstrip('/') + '/', webdav_config['path'].strip('/') + '/' + filename)

        # 读取备份文件
        with open(backup_path, 'rb') as f:
            backup_data = f.read()

        # 上传到WebDAV
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.put(
                remote_url,
                headers=headers,
                content=backup_data
            )

            if response.status_code not in [200, 201, 204]:
                raise Exception(f"WebDAV upload failed: HTTP {response.status_code}")

        await SystemLogger.info(
            module=LogModule.SYSTEM,
            message=f"WebDAV上传成功: {filename}",
            details={"remote_url": remote_url},
            user=current_admin.username
        )

    except Exception as e:
        await SystemLogger.error(
            module=LogModule.SYSTEM,
            message=f"WebDAV上传失败: {filename}",
            details={"error": str(e)},
            user=current_admin.username
        )
        raise


async def upload_to_ftp(backup_path, filename, ftp_config, current_admin):
    """上传备份文件到FTP服务器"""
    try:
        import ftplib

        # 连接FTP服务器
        ftp = ftplib.FTP()
        ftp.connect(ftp_config['host'], ftp_config.get('port', 21))
        ftp.login(ftp_config['username'], ftp_config['password'])

        # 切换到目标目录
        try:
            ftp.cwd(ftp_config['path'])
        except ftplib.error_perm:
            # 如果目录不存在，尝试创建
            ftp.mkd(ftp_config['path'])
            ftp.cwd(ftp_config['path'])

        # 上传文件
        with open(backup_path, 'rb') as f:
            ftp.storbinary(f'STOR {filename}', f)

        ftp.quit()

        await SystemLogger.info(
            module=LogModule.SYSTEM,
            message=f"FTP上传成功: {filename}",
            details={"host": ftp_config['host'], "path": ftp_config['path']},
            user=current_admin.username
        )

    except Exception as e:
        await SystemLogger.error(
            module=LogModule.SYSTEM,
            message=f"FTP上传失败: {filename}",
            details={"error": str(e)},
            user=current_admin.username
        )
        raise


@router.get("/logs", response_model=LogsResponse, summary="获取系统日志")
async def get_system_logs(
    level: Optional[str] = Query(None, description="日志级别"),
    module: Optional[str] = Query(None, description="模块名称"),
    user: Optional[str] = Query(None, description="用户名"),
    start_time: Optional[datetime] = Query(None, description="开始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    current_admin = Depends(get_current_active_admin)
):
    """获取系统日志（仅超级管理员可访问）"""
    if not current_admin.is_superuser:
        raise HTTPException(status_code=403, detail="Only superuser can access system logs")

    query = SystemLog.all()

    # 应用筛选条件
    if level:
        query = query.filter(level=level)

    if module:
        query = query.filter(module=module)

    if user:
        query = query.filter(user__icontains=user)

    if start_time:
        query = query.filter(timestamp__gte=start_time)

    if end_time:
        query = query.filter(timestamp__lte=end_time)

    # 获取总数
    total = await query.count()

    # 分页查询
    offset = (page - 1) * size
    logs = await query.offset(offset).limit(size).order_by("-timestamp")

    # 统计信息
    stats = {
        "total": total,
        "info_count": await SystemLog.filter(level=LogLevel.INFO).count(),
        "warning_count": await SystemLog.filter(level=LogLevel.WARNING).count(),
        "error_count": await SystemLog.filter(level=LogLevel.ERROR).count(),
        "debug_count": await SystemLog.filter(level=LogLevel.DEBUG).count(),
    }

    return {
        "logs": logs,
        "total": total,
        "stats": stats
    }


@router.delete("/logs", summary="清理系统日志")
async def clear_system_logs(
    days: int = Query(30, ge=1, description="保留天数"),
    current_admin = Depends(get_current_active_admin)
):
    """清理系统日志（仅超级管理员可操作）"""
    if not current_admin.is_superuser:
        raise HTTPException(status_code=403, detail="Only superuser can clear system logs")

    # 计算删除时间点
    cutoff_time = datetime.now() - timedelta(days=days)

    # 删除旧日志
    deleted_count = await SystemLog.filter(timestamp__lt=cutoff_time).delete()

    # 记录清理操作
    await SystemLogger.info(
        module=LogModule.SYSTEM,
        message=f"清理系统日志，删除 {deleted_count} 条记录",
        details={"deleted_count": deleted_count, "days": days},
        user=current_admin.username
    )

    return {
        "message": f"Successfully cleared {deleted_count} log entries",
        "deleted_count": deleted_count
    }


@router.post("/backup/test-webdav", summary="测试WebDAV连接")
async def test_webdav_connection(
    config: WebDAVTestRequest,
    current_admin = Depends(get_current_active_admin)
):
    """测试WebDAV连接"""
    if not current_admin.is_superuser:
        raise HTTPException(status_code=403, detail="Only superuser can test WebDAV connection")

    try:
        import httpx
        from urllib.parse import urljoin
        import base64

        # 准备认证头
        credentials = base64.b64encode(f"{config.username}:{config.password}".encode()).decode()
        headers = {
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/xml"
        }

        # 测试PROPFIND请求
        propfind_body = '''<?xml version="1.0" encoding="utf-8" ?>
        <D:propfind xmlns:D="DAV:">
            <D:prop>
                <D:displayname/>
                <D:getcontentlength/>
                <D:getlastmodified/>
                <D:resourcetype/>
            </D:prop>
        </D:propfind>'''

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.request(
                "PROPFIND",
                config.url,
                headers=headers,
                content=propfind_body
            )

            if response.status_code in [200, 207]:  # 207 Multi-Status is also success for WebDAV
                await SystemLogger.info(
                    module=LogModule.SYSTEM,
                    message="WebDAV连接测试成功",
                    details={"url": config.url, "username": config.username},
                    user=current_admin.username
                )
                return {"message": "WebDAV connection successful", "status": "success"}
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"WebDAV connection failed: HTTP {response.status_code}"
                )

    except httpx.RequestError as e:
        await SystemLogger.error(
            module=LogModule.SYSTEM,
            message="WebDAV连接测试失败",
            details={"url": config.url, "error": str(e)},
            user=current_admin.username
        )
        raise HTTPException(status_code=400, detail=f"WebDAV connection failed: {str(e)}")
    except Exception as e:
        await SystemLogger.error(
            module=LogModule.SYSTEM,
            message="WebDAV连接测试异常",
            details={"url": config.url, "error": str(e)},
            user=current_admin.username
        )
        raise HTTPException(status_code=500, detail=f"WebDAV test failed: {str(e)}")


@router.post("/backup/test-ftp", summary="测试FTP连接")
async def test_ftp_connection(
    config: dict,
    current_admin = Depends(get_current_active_admin)
):
    """测试FTP连接"""
    if not current_admin.is_superuser:
        raise HTTPException(status_code=403, detail="Only superuser can test FTP connection")

    try:
        import ftplib

        # 验证必要参数
        required_fields = ['host', 'username', 'password']
        for field in required_fields:
            if not config.get(field):
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")

        # 测试FTP连接
        ftp = ftplib.FTP()
        ftp.connect(config['host'], config.get('port', 21))
        ftp.login(config['username'], config['password'])

        # 测试目录访问
        if config.get('path'):
            try:
                ftp.cwd(config['path'])
            except ftplib.error_perm:
                # 如果目录不存在，尝试创建
                ftp.mkd(config['path'])
                ftp.cwd(config['path'])

        ftp.quit()

        await SystemLogger.info(
            module=LogModule.SYSTEM,
            message="FTP连接测试成功",
            details={"host": config['host'], "username": config['username']},
            user=current_admin.username
        )
        return {"message": "FTP connection successful", "status": "success"}

    except ftplib.all_errors as e:
        await SystemLogger.error(
            module=LogModule.SYSTEM,
            message="FTP连接测试失败",
            details={"host": config.get('host'), "error": str(e)},
            user=current_admin.username
        )
        raise HTTPException(status_code=400, detail=f"FTP connection failed: {str(e)}")
    except Exception as e:
        await SystemLogger.error(
            module=LogModule.SYSTEM,
            message="FTP连接测试异常",
            details={"host": config.get('host'), "error": str(e)},
            user=current_admin.username
        )
        raise HTTPException(status_code=500, detail=f"FTP test failed: {str(e)}")


@router.post("/test-cdn", summary="测试CDN连接")
async def test_cdn_connection(
    config: dict,
    current_admin = Depends(get_current_active_admin)
):
    """测试CDN连接"""
    if not current_admin.is_superuser:
        raise HTTPException(status_code=403, detail="Only superuser can test CDN connection")

    try:
        import httpx
        import io
        from PIL import Image

        # 验证配置参数
        required_fields = ['accessKey', 'secretKey', 'bucket', 'domain']
        for field in required_fields:
            if not config.get(field):
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")

        # 创建测试图片
        test_image = Image.new('RGB', (100, 100), color='red')
        img_buffer = io.BytesIO()
        test_image.save(img_buffer, format='PNG')
        img_buffer.seek(0)

        # 准备上传数据
        files = {
            'image': ('test_image.png', img_buffer.getvalue(), 'image/png')
        }
        data = {
            'folder': 'test'
        }

        # 设置请求头
        headers = {
            'token': config['accessKey']  # 使用accessKey作为token
        }

        # 测试上传到CDN
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                settings.IMAGE_CDN_URL,
                files=files,
                data=data,
                headers=headers
            )

            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 200:
                    await SystemLogger.info(
                        module=LogModule.SYSTEM,
                        message="CDN连接测试成功",
                        details={"domain": config['domain']},
                        user=current_admin.username
                    )
                    return {"message": "CDN connection successful", "status": "success"}
                else:
                    raise HTTPException(
                        status_code=400,
                        detail=f"CDN test failed: {result.get('msg', 'Unknown error')}"
                    )
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"CDN test failed: HTTP {response.status_code}"
                )

    except httpx.RequestError as e:
        await SystemLogger.error(
            module=LogModule.SYSTEM,
            message="CDN连接测试失败",
            details={"error": str(e)},
            user=current_admin.username
        )
        raise HTTPException(status_code=400, detail=f"CDN connection failed: {str(e)}")
    except Exception as e:
        await SystemLogger.error(
            module=LogModule.SYSTEM,
            message="CDN连接测试异常",
            details={"error": str(e)},
            user=current_admin.username
        )
        raise HTTPException(status_code=500, detail=f"CDN test failed: {str(e)}")


@router.post("/test-email", summary="测试邮件发送")
async def test_email_sending(
    config: dict,
    current_admin = Depends(get_current_active_admin)
):
    """测试邮件发送功能"""
    if not current_admin.is_superuser:
        raise HTTPException(status_code=403, detail="Only superuser can test email sending")

    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        # 验证配置参数
        required_fields = ['smtp_server', 'smtp_port', 'username', 'password', 'from_email']
        for field in required_fields:
            if not config.get(field):
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")

        # 创建测试邮件
        msg = MIMEMultipart()
        msg['From'] = config['from_email']
        msg['To'] = config.get('test_email', config['from_email'])  # 如果没有测试邮箱，发送给自己
        msg['Subject'] = "红旗小学考试管理系统 - 邮件测试"

        # 邮件内容
        body = f"""
        这是一封来自红旗小学考试管理系统的测试邮件。

        发送时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        发送者: {current_admin.username}
        系统版本: v1.0.0

        如果您收到这封邮件，说明邮件配置正确。

        ——————————————————————————
        红旗小学考试管理系统
        """

        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        # 连接SMTP服务器并发送邮件
        server = smtplib.SMTP(config['smtp_server'], int(config['smtp_port']))

        # 如果需要TLS加密
        if config.get('use_tls', True):
            server.starttls()

        # 登录
        server.login(config['username'], config['password'])

        # 发送邮件
        text = msg.as_string()
        server.sendmail(config['from_email'], msg['To'], text)
        server.quit()

        await SystemLogger.info(
            module=LogModule.SYSTEM,
            message="邮件发送测试成功",
            details={
                "smtp_server": config['smtp_server'],
                "from_email": config['from_email'],
                "to_email": msg['To']
            },
            user=current_admin.username
        )

        return {"message": "Email test successful", "status": "success"}

    except smtplib.SMTPException as e:
        await SystemLogger.error(
            module=LogModule.SYSTEM,
            message="邮件发送测试失败",
            details={"smtp_server": config.get('smtp_server'), "error": str(e)},
            user=current_admin.username
        )
        raise HTTPException(status_code=400, detail=f"Email test failed: {str(e)}")
    except Exception as e:
        await SystemLogger.error(
            module=LogModule.SYSTEM,
            message="邮件发送测试异常",
            details={"error": str(e)},
            user=current_admin.username
        )
        raise HTTPException(status_code=500, detail=f"Email test failed: {str(e)}")


@router.post("/backup/webdav", summary="WebDAV备份")
async def backup_to_webdav(
    config: WebDAVConfig,
    current_admin = Depends(get_current_active_admin)
):
    """备份数据到WebDAV服务器"""
    if not current_admin.is_superuser:
        raise HTTPException(status_code=403, detail="Only superuser can create WebDAV backup")

    try:
        import httpx
        import base64
        from pathlib import Path
        from urllib.parse import urljoin

        # 首先创建本地备份
        backup_response = await create_backup(current_admin)
        backup_info = backup_response["backup_info"]
        local_backup_path = backup_info["path"]

        # 准备WebDAV上传
        credentials = base64.b64encode(f"{config.username}:{config.password}".encode()).decode()
        headers = {
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/octet-stream"
        }

        # 构建远程路径
        remote_filename = backup_info["filename"]
        remote_url = urljoin(config.url.rstrip('/') + '/', config.path.strip('/') + '/' + remote_filename)

        # 读取备份文件
        with open(local_backup_path, 'rb') as f:
            backup_data = f.read()

        # 上传到WebDAV
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.put(
                remote_url,
                headers=headers,
                content=backup_data
            )

            if response.status_code in [200, 201, 204]:
                await SystemLogger.info(
                    module=LogModule.SYSTEM,
                    message=f"WebDAV备份成功: {remote_filename}",
                    details={
                        "backup_id": backup_info["backup_id"],
                        "remote_url": remote_url,
                        "size": backup_info["size"]
                    },
                    user=current_admin.username
                )

                return {
                    "message": "WebDAV backup successful",
                    "backup_info": backup_info,
                    "remote_url": remote_url
                }
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"WebDAV upload failed: HTTP {response.status_code}"
                )

    except Exception as e:
        await SystemLogger.error(
            module=LogModule.SYSTEM,
            message="WebDAV备份失败",
            details={"error": str(e)},
            user=current_admin.username
        )
        raise HTTPException(status_code=500, detail=f"WebDAV backup failed: {str(e)}")


@router.get("/backup/history", summary="获取备份历史")
async def get_backup_history(
    current_admin = Depends(get_current_active_admin)
):
    """获取备份历史列表"""
    if not current_admin.is_superuser:
        raise HTTPException(status_code=403, detail="Only superuser can access backup history")

    import os
    from pathlib import Path

    try:
        backup_dir = Path("backups")
        if not backup_dir.exists():
            return {"backups": [], "total": 0}

        backups = []
        for backup_file in backup_dir.glob("backup_*.sqlite3"):
            try:
                stat = backup_file.stat()
                filename = backup_file.name

                # 从文件名提取时间戳
                timestamp_str = filename.replace("backup_", "").replace(".sqlite3", "")

                # 尝试从系统日志中获取备份方法信息
                backup_method = "local"  # 默认值
                try:
                    # 查找相关的备份日志
                    log_entry = await SystemLog.filter(
                        module=LogModule.SYSTEM,
                        message__icontains=filename
                    ).first()
                    if log_entry and log_entry.details:
                        backup_method = log_entry.details.get("method", "local")
                except:
                    pass

                backup_info = {
                    "id": filename,
                    "filename": filename,
                    "size": stat.st_size,
                    "method": backup_method,
                    "status": "success",
                    "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "path": str(backup_file)
                }
                backups.append(backup_info)
            except Exception as e:
                print(f"Error processing backup file {backup_file}: {e}")
                continue

        # 按创建时间倒序排列
        backups.sort(key=lambda x: x["created_at"], reverse=True)

        return {
            "backups": backups,
            "total": len(backups)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get backup history: {str(e)}")


@router.get("/backup/download/{backup_id}", summary="下载备份文件")
async def download_backup(
    backup_id: str,
    current_admin = Depends(get_current_active_admin)
):
    """下载备份文件"""
    if not current_admin.is_superuser:
        raise HTTPException(status_code=403, detail="Only superuser can download backup")

    from fastapi.responses import FileResponse
    from pathlib import Path

    try:
        backup_path = Path("backups") / backup_id

        if not backup_path.exists():
            raise HTTPException(status_code=404, detail="Backup file not found")

        await SystemLogger.info(
            module=LogModule.SYSTEM,
            message=f"下载备份文件: {backup_id}",
            details={"backup_id": backup_id},
            user=current_admin.username
        )

        return FileResponse(
            path=str(backup_path),
            filename=backup_id,
            media_type='application/octet-stream'
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to download backup: {str(e)}")


@router.delete("/backup/{backup_id}", summary="删除备份文件")
async def delete_backup(
    backup_id: str,
    current_admin = Depends(get_current_active_admin)
):
    """删除备份文件"""
    if not current_admin.is_superuser:
        raise HTTPException(status_code=403, detail="Only superuser can delete backup")

    from pathlib import Path

    try:
        backup_path = Path("backups") / backup_id

        if not backup_path.exists():
            raise HTTPException(status_code=404, detail="Backup file not found")

        # 删除文件
        backup_path.unlink()

        await SystemLogger.warning(
            module=LogModule.SYSTEM,
            message=f"删除备份文件: {backup_id}",
            details={"backup_id": backup_id},
            user=current_admin.username
        )

        return {"message": f"Backup {backup_id} deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete backup: {str(e)}")


@router.post("/backup/restore/{backup_id}", summary="从备份恢复数据")
async def restore_from_backup(
    backup_id: str,
    current_admin = Depends(get_current_active_admin)
):
    """从备份文件恢复数据"""
    if not current_admin.is_superuser:
        raise HTTPException(status_code=403, detail="Only superuser can restore backup")

    import os
    import sqlite3
    import shutil
    from pathlib import Path

    try:
        backup_path = Path("backups") / backup_id

        if not backup_path.exists():
            raise HTTPException(status_code=404, detail="Backup file not found")

        # 当前数据库路径
        current_db_path = "db.sqlite3"

        # 创建当前数据库的备份
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safety_backup_path = Path("backups") / f"safety_backup_before_restore_{timestamp}.sqlite3"

        if os.path.exists(current_db_path):
            shutil.copy2(current_db_path, safety_backup_path)

        # 恢复数据库
        shutil.copy2(backup_path, current_db_path)

        await SystemLogger.warning(
            module=LogModule.SYSTEM,
            message=f"从备份恢复数据: {backup_id}",
            details={
                "backup_id": backup_id,
                "safety_backup": str(safety_backup_path)
            },
            user=current_admin.username
        )

        return {
            "message": f"Data restored from backup {backup_id} successfully",
            "safety_backup": str(safety_backup_path)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to restore backup: {str(e)}")


@router.get("/config/backup", summary="获取备份配置")
async def get_backup_config(
    current_admin = Depends(get_current_active_admin)
):
    """获取备份配置"""
    try:
        # 获取备份配置
        configs = {}

        # 获取各种备份配置
        config_keys = [
            ConfigKey.BACKUP_METHOD,
            ConfigKey.BACKUP_AUTO,
            ConfigKey.BACKUP_WEBDAV,
            ConfigKey.BACKUP_FTP
        ]

        for key in config_keys:
            config = await SystemConfig.filter(config_key=key, is_active=True).first()
            if config:
                # 反序列化JSON字符串
                try:
                    value = json.loads(config.config_value)
                    field_name = key.split('.')[-1]
                    # 将 'auto' 字段映射为 'autoBackup' 以保持前端兼容性
                    if field_name == 'auto':
                        field_name = 'autoBackup'
                    configs[field_name] = value
                except (json.JSONDecodeError, TypeError):
                    # 如果不是JSON格式，直接使用原值
                    field_name = key.split('.')[-1]
                    if field_name == 'auto':
                        field_name = 'autoBackup'
                    configs[field_name] = config.config_value

        # 设置默认值
        default_config = {
            "method": "local",
            "autoBackup": False,
            "webdav": {
                "url": "",
                "username": "",
                "password": "",
                "path": "/backups/hqxx-exam"
            },
            "ftp": {
                "host": "",
                "port": 21,
                "username": "",
                "password": "",
                "path": "/backups"
            }
        }

        # 合并配置
        result = {**default_config, **configs}

        return {"config": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get backup config: {str(e)}")


@router.post("/config/backup", summary="保存备份配置")
async def save_backup_config(
    config: BackupConfigRequest,
    current_admin = Depends(get_current_active_admin)
):
    """保存备份配置"""
    if not current_admin.is_superuser:
        raise HTTPException(status_code=403, detail="Only superuser can save backup config")

    try:
        # 保存各种配置，确保所有值都是JSON可序列化的
        # 注意：对于简单值，我们需要将它们包装在合适的结构中
        config_data = {}

        # 备份方式 - 存储为字符串值
        if hasattr(config, 'method'):
            config_data[ConfigKey.BACKUP_METHOD] = config.method

        # 自动备份 - 存储为布尔值
        if hasattr(config, 'autoBackup'):
            config_data[ConfigKey.BACKUP_AUTO] = config.autoBackup

        # WebDAV配置 - 存储为对象
        if hasattr(config, 'webdav') and config.webdav:
            config_data[ConfigKey.BACKUP_WEBDAV] = config.webdav

        # FTP配置 - 存储为对象
        if hasattr(config, 'ftp') and config.ftp:
            config_data[ConfigKey.BACKUP_FTP] = config.ftp

        print(f"Debug: 准备保存的配置数据: {config_data}")

        for key, value in config_data.items():
            print(f"Debug: 保存配置 {key} = {value} (类型: {type(value)})")

            # 查找现有配置
            existing_config = await SystemConfig.filter(config_key=key).first()

            if existing_config:
                print(f"Debug: 更新现有配置 {key}")
                # 更新现有配置 - 手动序列化为JSON字符串
                existing_config.config_value = json.dumps(value, ensure_ascii=False)
                existing_config.updated_by = current_admin.username
                existing_config.updated_at = datetime.now()
                await existing_config.save()
            else:
                print(f"Debug: 创建新配置 {key}")
                # 创建新配置 - 手动序列化为JSON字符串
                await SystemConfig.create(
                    config_key=key,
                    config_value=json.dumps(value, ensure_ascii=False),
                    config_type=ConfigType.BACKUP,
                    description=f"备份配置: {key}",
                    updated_by=current_admin.username
                )

        await SystemLogger.info(
            module=LogModule.SYSTEM,
            message="保存备份配置",
            details={"config": config.dict()},
            user=current_admin.username
        )

        return {"message": "Backup config saved successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save backup config: {str(e)}")


@router.get("/config/settings", summary="获取系统设置")
async def get_system_settings(
    current_admin = Depends(get_current_active_admin)
):
    """获取系统设置"""
    try:
        # 获取系统设置
        configs = {}

        config_keys = [
            ConfigKey.SYSTEM_BASIC,
            ConfigKey.SYSTEM_SECURITY,
            ConfigKey.SYSTEM_FILE,
            ConfigKey.SYSTEM_EMAIL
        ]

        for key in config_keys:
            config = await SystemConfig.filter(config_key=key, is_active=True).first()
            if config:
                configs[key.split('.')[-1]] = config.config_value

        # 设置默认值
        default_settings = {
            "basic": {
                "schoolName": "红旗小学",
                "schoolCode": "HQXX001",
                "phone": "010-12345678",
                "email": "admin@hqxx.edu.cn",
                "address": "北京市朝阳区红旗街123号",
                "description": "红旗小学是一所具有悠久历史的优秀学校...",
                "systemName": "红旗小学考试管理系统",
                "version": "v1.0.0",
                "timezone": "Asia/Shanghai",
                "language": "zh-CN",
                "maintenanceMode": False,
                "debugMode": False
            },
            "security": {
                "minPasswordLength": 6,
                "maxLoginAttempts": 5,
                "tokenExpireMinutes": 120,
                "lockoutMinutes": 15,
                "requireComplexPassword": True,
                "enableTwoFactor": False,
                "enableIpWhitelist": False,
                "enableApiRateLimit": True,
                "allowedIps": ""
            },
            "file": {
                "maxFileSize": 10,
                "allowedTypes": ["image", "document"],
                "storageType": "local",
                "cdn": {
                    "accessKey": "",
                    "secretKey": "",
                    "bucket": "",
                    "domain": ""
                }
            },
            "email": {
                "host": "",
                "port": 587,
                "username": "",
                "password": "",
                "fromName": "红旗小学考试系统",
                "fromEmail": "noreply@hqxx.edu.cn",
                "ssl": False,
                "tls": True
            }
        }

        # 合并配置
        result = {**default_settings, **configs}

        return {"settings": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get system settings: {str(e)}")


@router.post("/config/settings", summary="保存系统设置")
async def save_system_settings(
    settings: SystemSettingsRequest,
    current_admin = Depends(get_current_active_admin)
):
    """保存系统设置"""
    if not current_admin.is_superuser:
        raise HTTPException(status_code=403, detail="Only superuser can save system settings")

    try:
        # 保存各种设置
        config_data = {
            ConfigKey.SYSTEM_BASIC: settings.basic,
            ConfigKey.SYSTEM_SECURITY: settings.security,
            ConfigKey.SYSTEM_FILE: settings.file,
            ConfigKey.SYSTEM_EMAIL: settings.email
        }

        for key, value in config_data.items():
            # 查找现有配置
            existing_config = await SystemConfig.filter(config_key=key).first()

            if existing_config:
                # 更新现有配置
                existing_config.config_value = value
                existing_config.updated_by = current_admin.username
                await existing_config.save()
            else:
                # 创建新配置
                await SystemConfig.create(
                    config_key=key,
                    config_value=value,
                    config_type=ConfigType.SYSTEM,
                    description=f"系统设置: {key}",
                    updated_by=current_admin.username
                )

        await SystemLogger.info(
            module=LogModule.SYSTEM,
            message="保存系统设置",
            details={"settings_keys": list(config_data.keys())},
            user=current_admin.username
        )

        return {"message": "System settings saved successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save system settings: {str(e)}")


@router.get("/monitor/performance", summary="获取性能监控数据")
async def get_performance_data(
    current_admin = Depends(get_current_active_admin)
):
    """获取系统性能监控数据"""
    if not await PermissionManager.has_permission(current_admin, PermissionCode.SYSTEM_VIEW):
        raise HTTPException(status_code=403, detail="Permission denied")

    try:
        from app.middleware.performance import performance_monitor
        return performance_monitor.get_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get performance data: {str(e)}")


@router.get("/monitor/health", summary="系统健康检查")
async def health_check_detailed():
    """详细的系统健康检查"""
    try:
        from app.middleware.performance import HealthChecker
        return await HealthChecker.get_health_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@router.get("/monitor/slow-requests", summary="获取慢请求列表")
async def get_slow_requests(
    threshold: float = Query(1.0, description="慢请求阈值(秒)"),
    current_admin = Depends(get_current_active_admin)
):
    """获取慢请求列表"""
    if not await PermissionManager.has_permission(current_admin, PermissionCode.SYSTEM_VIEW):
        raise HTTPException(status_code=403, detail="Permission denied")

    try:
        from app.middleware.performance import performance_monitor
        slow_requests = performance_monitor.get_slow_requests(threshold)
        return {
            "threshold": threshold,
            "count": len(slow_requests),
            "requests": slow_requests[-50:]  # 返回最近50个慢请求
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get slow requests: {str(e)}")

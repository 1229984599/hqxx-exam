from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from app.models.subject import Subject
from app.schemas.common import (
    SubjectCreate, SubjectUpdate, SubjectResponse,
    MessageResponse, BatchUpdateRequest, BatchDeleteRequest,
    BatchCopyRequest, BatchOperationResponse
)
from app.dependencies.auth import get_current_active_admin
from app.utils.permissions import PermissionManager
from app.models.role import PermissionCode

router = APIRouter(prefix="/subjects", tags=["学科管理"])


@router.get("/", response_model=List[SubjectResponse], summary="获取学科列表")
async def get_subjects(
    is_active: bool = Query(None, description="是否激活"),
    search: str = Query(None, description="搜索关键词"),
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(100, ge=1, le=100, description="限制数量")
):
    """获取学科列表"""
    query = Subject.all()
    
    if is_active is not None:
        query = query.filter(is_active=is_active)

    if search:
        query = query.filter(name__icontains=search) | query.filter(code__icontains=search)

    subjects = await query.offset(skip).limit(limit).order_by("sort_order", "id")
    return subjects


@router.get("/{subject_id}", response_model=SubjectResponse, summary="获取学科详情")
async def get_subject(subject_id: int):
    """获取学科详情"""
    subject = await Subject.filter(id=subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return subject


@router.post("/", response_model=SubjectResponse, summary="创建学科")
async def create_subject(
    subject_data: SubjectCreate,
    current_admin = Depends(get_current_active_admin)
):
    """创建学科"""
    # 检查权限
    if not current_admin.is_superuser and not await PermissionManager.has_permission(current_admin, PermissionCode.BASIC_DATA_EDIT):
        raise HTTPException(status_code=403, detail="Permission denied")

    # 检查代码是否已存在
    existing = await Subject.filter(code=subject_data.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Subject code already exists")
    
    subject = await Subject.create(**subject_data.dict())
    return subject


@router.put("/{subject_id}", response_model=SubjectResponse, summary="更新学科")
async def update_subject(
    subject_id: int,
    subject_data: SubjectUpdate,
    current_admin = Depends(get_current_active_admin)
):
    """更新学科"""
    # 检查权限
    if not current_admin.is_superuser and not await PermissionManager.has_permission(current_admin, PermissionCode.BASIC_DATA_EDIT):
        raise HTTPException(status_code=403, detail="Permission denied")

    subject = await Subject.filter(id=subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    # 检查代码是否与其他学科冲突
    if subject_data.code:
        existing = await Subject.filter(code=subject_data.code).exclude(id=subject_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Subject code already exists")
    
    # 更新学科数据
    update_data = subject_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(subject, field, value)
    await subject.save()
    return subject


@router.delete("/{subject_id}", response_model=MessageResponse, summary="删除学科")
async def delete_subject(
    subject_id: int,
    current_admin = Depends(get_current_active_admin)
):
    """删除学科"""
    # 检查权限
    if not current_admin.is_superuser and not await PermissionManager.has_permission(current_admin, PermissionCode.BASIC_DATA_EDIT):
        raise HTTPException(status_code=403, detail="Permission denied")

    subject = await Subject.filter(id=subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    await subject.delete()
    return {"message": "Subject deleted successfully"}


@router.post("/batch-update", response_model=BatchOperationResponse, summary="批量更新学科")
async def batch_update_subjects(
    request: BatchUpdateRequest,
    current_admin = Depends(get_current_active_admin)
):
    """批量更新学科"""
    # 检查权限
    if not current_admin.is_superuser and not await PermissionManager.has_permission(current_admin, PermissionCode.BASIC_DATA_EDIT):
        raise HTTPException(status_code=403, detail="Permission denied")

    success_count = 0
    failed_count = 0
    failed_items = []

    for subject_id in request.get_ids():
        try:
            subject = await Subject.filter(id=subject_id).first()
            if not subject:
                failed_count += 1
                failed_items.append({"id": subject_id, "error": "Subject not found"})
                continue

            # 更新学科数据
            for field, value in request.update_data.items():
                if hasattr(subject, field):
                    setattr(subject, field, value)

            await subject.save()
            success_count += 1
        except Exception as e:
            failed_count += 1
            failed_items.append({"id": subject_id, "error": str(e)})

    return BatchOperationResponse(
        success_count=success_count,
        failed_count=failed_count,
        total_count=len(request.get_ids()),
        message=f"批量更新完成：成功 {success_count} 个，失败 {failed_count} 个",
        failed_items=failed_items
    )


@router.post("/batch-delete", response_model=BatchOperationResponse, summary="批量删除学科")
async def batch_delete_subjects(
    request: BatchDeleteRequest,
    current_admin = Depends(get_current_active_admin)
):
    """批量删除学科"""
    # 检查权限
    if not current_admin.is_superuser and not await PermissionManager.has_permission(current_admin, PermissionCode.BASIC_DATA_EDIT):
        raise HTTPException(status_code=403, detail="Permission denied")

    success_count = 0
    failed_count = 0
    failed_items = []

    for subject_id in request.get_ids():
        try:
            subject = await Subject.filter(id=subject_id).first()
            if not subject:
                failed_count += 1
                failed_items.append({"id": subject_id, "error": "Subject not found"})
                continue

            await subject.delete()
            success_count += 1
        except Exception as e:
            failed_count += 1
            failed_items.append({"id": subject_id, "error": str(e)})

    return BatchOperationResponse(
        success_count=success_count,
        failed_count=failed_count,
        total_count=len(request.get_ids()),
        message=f"批量删除完成：成功 {success_count} 个，失败 {failed_count} 个",
        failed_items=failed_items
    )


@router.post("/batch-copy", response_model=BatchOperationResponse, summary="批量复制学科")
async def batch_copy_subjects(
    request: BatchCopyRequest,
    current_admin = Depends(get_current_active_admin)
):
    """批量复制学科"""
    # 检查权限
    if not current_admin.is_superuser and not await PermissionManager.has_permission(current_admin, PermissionCode.BASIC_DATA_EDIT):
        raise HTTPException(status_code=403, detail="Permission denied")

    success_count = 0
    failed_count = 0
    failed_items = []
    copy_count = request.copy_data.get('copy_count', 1)
    name_suffix = request.copy_data.get('name_suffix', '_副本')

    for subject_id in request.get_ids():
        try:
            subject = await Subject.filter(id=subject_id).first()
            if not subject:
                failed_count += 1
                failed_items.append({"id": subject_id, "error": "Subject not found"})
                continue

            for i in range(copy_count):
                # 创建副本
                copy_name = f"{subject.name}{name_suffix}"
                if copy_count > 1:
                    copy_name += f"_{i+1}"

                copy_code = f"{subject.code}_copy"
                if copy_count > 1:
                    copy_code += f"_{i+1}"

                # 确保代码唯一性
                counter = 1
                original_copy_code = copy_code
                while await Subject.filter(code=copy_code).exists():
                    copy_code = f"{original_copy_code}_{counter}"
                    counter += 1

                await Subject.create(
                    name=copy_name,
                    code=copy_code,
                    icon=subject.icon,
                    color=subject.color,
                    is_active=subject.is_active,
                    sort_order=subject.sort_order,
                    description=subject.description
                )
                success_count += 1
        except Exception as e:
            failed_count += 1
            failed_items.append({"id": subject_id, "error": str(e)})

    return BatchOperationResponse(
        success_count=success_count,
        failed_count=failed_count,
        total_count=len(request.get_ids()) * copy_count,
        message=f"批量复制完成：成功 {success_count} 个，失败 {failed_count} 个",
        failed_items=failed_items
    )

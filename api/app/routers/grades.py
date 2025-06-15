from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from app.models.grade import Grade
from app.schemas.common import (
    GradeCreate, GradeUpdate, GradeResponse,
    MessageResponse, BatchUpdateRequest, BatchDeleteRequest,
    BatchCopyRequest, BatchOperationResponse
)
from app.dependencies.auth import get_current_active_admin
from app.utils.permissions import PermissionManager
from app.models.role import PermissionCode

router = APIRouter(prefix="/grades", tags=["年级管理"])


@router.get("/", response_model=List[GradeResponse], summary="获取年级列表")
async def get_grades(
    is_active: bool = Query(None, description="是否激活"),
    level: int = Query(None, description="年级级别"),
    search: str = Query(None, description="搜索关键词"),
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(100, ge=1, le=100, description="限制数量")
):
    """获取年级列表"""
    query = Grade.all()
    
    if is_active is not None:
        query = query.filter(is_active=is_active)

    if level is not None:
        query = query.filter(level=level)

    if search:
        query = query.filter(name__icontains=search) | query.filter(code__icontains=search)

    grades = await query.offset(skip).limit(limit).order_by("sort_order", "level")
    return grades


@router.get("/{grade_id}", response_model=GradeResponse, summary="获取年级详情")
async def get_grade(grade_id: int):
    """获取年级详情"""
    grade = await Grade.filter(id=grade_id).first()
    if not grade:
        raise HTTPException(status_code=404, detail="Grade not found")
    return grade


@router.post("/", response_model=GradeResponse, summary="创建年级")
async def create_grade(
    grade_data: GradeCreate,
    current_admin = Depends(get_current_active_admin)
):
    """创建年级"""
    # 检查权限
    if not current_admin.is_superuser and not await PermissionManager.has_permission(current_admin, PermissionCode.BASIC_DATA_EDIT):
        raise HTTPException(status_code=403, detail="Permission denied")

    # 检查代码是否已存在
    existing = await Grade.filter(code=grade_data.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Grade code already exists")
    
    grade = await Grade.create(**grade_data.dict())
    return grade


@router.put("/{grade_id}", response_model=GradeResponse, summary="更新年级")
async def update_grade(
    grade_id: int,
    grade_data: GradeUpdate,
    current_admin = Depends(get_current_active_admin)
):
    """更新年级"""
    # 检查权限
    if not current_admin.is_superuser and not await PermissionManager.has_permission(current_admin, PermissionCode.BASIC_DATA_EDIT):
        raise HTTPException(status_code=403, detail="Permission denied")

    grade = await Grade.filter(id=grade_id).first()
    if not grade:
        raise HTTPException(status_code=404, detail="Grade not found")
    
    # 检查代码是否与其他年级冲突
    if grade_data.code:
        existing = await Grade.filter(code=grade_data.code).exclude(id=grade_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Grade code already exists")
    
    # 更新年级数据
    update_data = grade_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(grade, field, value)
    await grade.save()
    return grade


@router.delete("/{grade_id}", response_model=MessageResponse, summary="删除年级")
async def delete_grade(
    grade_id: int,
    current_admin = Depends(get_current_active_admin)
):
    """删除年级"""
    # 检查权限
    if not current_admin.is_superuser and not await PermissionManager.has_permission(current_admin, PermissionCode.BASIC_DATA_EDIT):
        raise HTTPException(status_code=403, detail="Permission denied")

    grade = await Grade.filter(id=grade_id).first()
    if not grade:
        raise HTTPException(status_code=404, detail="Grade not found")
    
    await grade.delete()
    return {"message": "Grade deleted successfully"}


@router.post("/batch-update", response_model=BatchOperationResponse, summary="批量更新年级")
async def batch_update_grades(
    request: BatchUpdateRequest,
    current_admin = Depends(get_current_active_admin)
):
    """批量更新年级"""
    # 检查权限
    if not current_admin.is_superuser and not await PermissionManager.has_permission(current_admin, PermissionCode.BASIC_DATA_EDIT):
        raise HTTPException(status_code=403, detail="Permission denied")

    success_count = 0
    failed_count = 0
    failed_items = []

    for grade_id in request.get_ids():
        try:
            grade = await Grade.filter(id=grade_id).first()
            if not grade:
                failed_count += 1
                failed_items.append({"id": grade_id, "error": "Grade not found"})
                continue

            # 更新年级数据
            for field, value in request.update_data.items():
                if hasattr(grade, field):
                    setattr(grade, field, value)

            await grade.save()
            success_count += 1
        except Exception as e:
            failed_count += 1
            failed_items.append({"id": grade_id, "error": str(e)})

    return BatchOperationResponse(
        success_count=success_count,
        failed_count=failed_count,
        total_count=len(request.get_ids()),
        message=f"批量更新完成：成功 {success_count} 个，失败 {failed_count} 个",
        failed_items=failed_items
    )


@router.post("/batch-delete", response_model=BatchOperationResponse, summary="批量删除年级")
async def batch_delete_grades(
    request: BatchDeleteRequest,
    current_admin = Depends(get_current_active_admin)
):
    """批量删除年级"""
    # 检查权限
    if not current_admin.is_superuser and not await PermissionManager.has_permission(current_admin, PermissionCode.BASIC_DATA_EDIT):
        raise HTTPException(status_code=403, detail="Permission denied")

    success_count = 0
    failed_count = 0
    failed_items = []

    for grade_id in request.get_ids():
        try:
            grade = await Grade.filter(id=grade_id).first()
            if not grade:
                failed_count += 1
                failed_items.append({"id": grade_id, "error": "Grade not found"})
                continue

            await grade.delete()
            success_count += 1
        except Exception as e:
            failed_count += 1
            failed_items.append({"id": grade_id, "error": str(e)})

    return BatchOperationResponse(
        success_count=success_count,
        failed_count=failed_count,
        total_count=len(request.get_ids()),
        message=f"批量删除完成：成功 {success_count} 个，失败 {failed_count} 个",
        failed_items=failed_items
    )


@router.post("/batch-copy", response_model=BatchOperationResponse, summary="批量复制年级")
async def batch_copy_grades(
    request: BatchCopyRequest,
    current_admin = Depends(get_current_active_admin)
):
    """批量复制年级"""
    # 检查权限
    if not current_admin.is_superuser and not await PermissionManager.has_permission(current_admin, PermissionCode.BASIC_DATA_EDIT):
        raise HTTPException(status_code=403, detail="Permission denied")

    success_count = 0
    failed_count = 0
    failed_items = []
    copy_count = request.copy_data.get('copy_count', 1)
    name_suffix = request.copy_data.get('name_suffix', '_副本')

    for grade_id in request.get_ids():
        try:
            grade = await Grade.filter(id=grade_id).first()
            if not grade:
                failed_count += 1
                failed_items.append({"id": grade_id, "error": "Grade not found"})
                continue

            for i in range(copy_count):
                # 创建副本
                copy_name = f"{grade.name}{name_suffix}"
                if copy_count > 1:
                    copy_name += f"_{i+1}"

                copy_code = f"{grade.code}_copy"
                if copy_count > 1:
                    copy_code += f"_{i+1}"

                # 确保代码唯一性
                counter = 1
                original_copy_code = copy_code
                while await Grade.filter(code=copy_code).exists():
                    copy_code = f"{original_copy_code}_{counter}"
                    counter += 1

                await Grade.create(
                    name=copy_name,
                    code=copy_code,
                    level=grade.level,
                    is_active=grade.is_active,
                    sort_order=grade.sort_order,
                    description=grade.description
                )
                success_count += 1
        except Exception as e:
            failed_count += 1
            failed_items.append({"id": grade_id, "error": str(e)})

    return BatchOperationResponse(
        success_count=success_count,
        failed_count=failed_count,
        total_count=len(request.get_ids()) * copy_count,
        message=f"批量复制完成：成功 {success_count} 个，失败 {failed_count} 个",
        failed_items=failed_items
    )

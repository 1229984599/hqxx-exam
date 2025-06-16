from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from app.models.semester import Semester
from app.schemas.common import (
    SemesterCreate, SemesterUpdate, SemesterResponse,
    PaginatedResponse, MessageResponse, BatchUpdateRequest,
    BatchDeleteRequest, BatchCopyRequest, BatchOperationResponse
)
from app.dependencies.auth import get_current_active_admin
from app.utils.permissions import PermissionManager
from app.models.role import PermissionCode

router = APIRouter(prefix="/semesters", tags=["学期管理"])


@router.get("/", response_model=List[SemesterResponse], summary="获取学期列表")
async def get_semesters(
    is_active: bool = Query(None, description="是否激活"),
    search: str = Query(None, description="搜索关键词"),
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(100, ge=1, le=100, description="限制数量")
):
    """获取学期列表"""
    query = Semester.all()

    if is_active is not None:
        query = query.filter(is_active=is_active)

    if search:
        query = query.filter(name__icontains=search) | query.filter(code__icontains=search)

    semesters = await query.offset(skip).limit(limit).order_by("sort_order", "id")

    # 手动转换日期字段
    result = []
    for semester in semesters:
        semester_dict = {
            "id": semester.id,
            "name": semester.name,
            "code": semester.code,
            "start_date": semester.start_date.isoformat() if semester.start_date else None,
            "end_date": semester.end_date.isoformat() if semester.end_date else None,
            "is_active": semester.is_active,
            "sort_order": semester.sort_order,
            "description": semester.description,
            "created_at": semester.created_at,
            "updated_at": semester.updated_at
        }
        result.append(semester_dict)

    return result


@router.get("/{semester_id}", response_model=SemesterResponse, summary="获取学期详情")
async def get_semester(semester_id: int):
    """获取学期详情"""
    semester = await Semester.filter(id=semester_id).first()
    if not semester:
        raise HTTPException(status_code=404, detail="Semester not found")

    return {
        "id": semester.id,
        "name": semester.name,
        "code": semester.code,
        "start_date": semester.start_date.isoformat() if semester.start_date else None,
        "end_date": semester.end_date.isoformat() if semester.end_date else None,
        "is_active": semester.is_active,
        "sort_order": semester.sort_order,
        "description": semester.description,
        "created_at": semester.created_at,
        "updated_at": semester.updated_at
    }


@router.post("/", response_model=SemesterResponse, summary="创建学期")
async def create_semester(
    semester_data: SemesterCreate,
    current_admin = Depends(get_current_active_admin)
):
    """创建学期"""
    # 检查权限
    if not current_admin.is_superuser and not await PermissionManager.has_permission(current_admin, PermissionCode.BASIC_DATA_EDIT):
        raise HTTPException(status_code=403, detail="Permission denied")
    # 检查代码是否已存在
    existing = await Semester.filter(code=semester_data.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Semester code already exists")
    
    semester = await Semester.create(**semester_data.dict())

    return {
        "id": semester.id,
        "name": semester.name,
        "code": semester.code,
        "start_date": semester.start_date.isoformat() if semester.start_date else None,
        "end_date": semester.end_date.isoformat() if semester.end_date else None,
        "is_active": semester.is_active,
        "sort_order": semester.sort_order,
        "description": semester.description,
        "created_at": semester.created_at,
        "updated_at": semester.updated_at
    }


@router.put("/{semester_id}", response_model=SemesterResponse, summary="更新学期")
async def update_semester(
    semester_id: int,
    semester_data: SemesterUpdate,
    current_admin = Depends(get_current_active_admin)
):
    """更新学期"""
    # 检查权限
    if not current_admin.is_superuser and not await PermissionManager.has_permission(current_admin, PermissionCode.BASIC_DATA_EDIT):
        raise HTTPException(status_code=403, detail="Permission denied")
    semester = await Semester.filter(id=semester_id).first()
    if not semester:
        raise HTTPException(status_code=404, detail="Semester not found")
    
    # 检查代码是否与其他学期冲突
    if semester_data.code:
        existing = await Semester.filter(code=semester_data.code).exclude(id=semester_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Semester code already exists")
    
    # 更新学期数据
    update_data = semester_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(semester, field, value)
    await semester.save()

    return {
        "id": semester.id,
        "name": semester.name,
        "code": semester.code,
        "start_date": semester.start_date.isoformat() if semester.start_date else None,
        "end_date": semester.end_date.isoformat() if semester.end_date else None,
        "is_active": semester.is_active,
        "sort_order": semester.sort_order,
        "description": semester.description,
        "created_at": semester.created_at,
        "updated_at": semester.updated_at
    }


@router.delete("/{semester_id}", response_model=MessageResponse, summary="删除学期")
async def delete_semester(
    semester_id: int,
    current_admin = Depends(get_current_active_admin)
):
    """删除学期"""
    # 检查权限
    if not current_admin.is_superuser and not await PermissionManager.has_permission(current_admin, PermissionCode.BASIC_DATA_EDIT):
        raise HTTPException(status_code=403, detail="Permission denied")
    semester = await Semester.filter(id=semester_id).first()
    if not semester:
        raise HTTPException(status_code=404, detail="Semester not found")
    
    await semester.delete()
    return {"message": "Semester deleted successfully"}


@router.post("/batch-update", response_model=BatchOperationResponse, summary="批量更新学期")
async def batch_update_semesters(
    request: BatchUpdateRequest,
    current_admin = Depends(get_current_active_admin)
):
    """批量更新学期"""
    # 检查权限
    if not current_admin.is_superuser and not await PermissionManager.has_permission(current_admin, PermissionCode.BASIC_DATA_EDIT):
        raise HTTPException(status_code=403, detail="Permission denied")

    success_count = 0
    failed_count = 0
    failed_items = []

    for semester_id in request.get_ids():
        try:
            semester = await Semester.filter(id=semester_id).first()
            if not semester:
                failed_count += 1
                failed_items.append({"id": semester_id, "error": "Semester not found"})
                continue

            # 更新学期数据
            for field, value in request.update_data.items():
                if hasattr(semester, field):
                    setattr(semester, field, value)

            await semester.save()
            success_count += 1
        except Exception as e:
            failed_count += 1
            failed_items.append({"id": semester_id, "error": str(e)})

    return BatchOperationResponse(
        success_count=success_count,
        failed_count=failed_count,
        total_count=len(request.get_ids()),
        message=f"批量更新完成：成功 {success_count} 个，失败 {failed_count} 个",
        failed_items=failed_items
    )


@router.post("/batch-delete", response_model=BatchOperationResponse, summary="批量删除学期")
async def batch_delete_semesters(
    request: BatchDeleteRequest,
    current_admin = Depends(get_current_active_admin)
):
    """批量删除学期"""
    # 检查权限
    if not current_admin.is_superuser and not await PermissionManager.has_permission(current_admin, PermissionCode.BASIC_DATA_EDIT):
        raise HTTPException(status_code=403, detail="Permission denied")

    success_count = 0
    failed_count = 0
    failed_items = []

    for semester_id in request.get_ids():
        try:
            semester = await Semester.filter(id=semester_id).first()
            if not semester:
                failed_count += 1
                failed_items.append({"id": semester_id, "error": "Semester not found"})
                continue

            await semester.delete()
            success_count += 1
        except Exception as e:
            failed_count += 1
            failed_items.append({"id": semester_id, "error": str(e)})

    return BatchOperationResponse(
        success_count=success_count,
        failed_count=failed_count,
        total_count=len(request.get_ids()),
        message=f"批量删除完成：成功 {success_count} 个，失败 {failed_count} 个",
        failed_items=failed_items
    )


@router.post("/batch-copy", response_model=BatchOperationResponse, summary="批量复制学期")
async def batch_copy_semesters(
    request: BatchCopyRequest,
    current_admin = Depends(get_current_active_admin)
):
    """批量复制学期"""
    # 检查权限
    if not current_admin.is_superuser and not await PermissionManager.has_permission(current_admin, PermissionCode.BASIC_DATA_EDIT):
        raise HTTPException(status_code=403, detail="Permission denied")

    success_count = 0
    failed_count = 0
    failed_items = []
    copy_count = request.copy_data.get('copy_count', 1)
    name_suffix = request.copy_data.get('name_suffix', '_副本')

    for semester_id in request.get_ids():
        try:
            semester = await Semester.filter(id=semester_id).first()
            if not semester:
                failed_count += 1
                failed_items.append({"id": semester_id, "error": "Semester not found"})
                continue

            for i in range(copy_count):
                # 创建副本
                copy_name = f"{semester.name}{name_suffix}"
                if copy_count > 1:
                    copy_name += f"_{i+1}"

                copy_code = f"{semester.code}_copy"
                if copy_count > 1:
                    copy_code += f"_{i+1}"

                # 确保代码唯一性
                counter = 1
                original_copy_code = copy_code
                while await Semester.filter(code=copy_code).exists():
                    copy_code = f"{original_copy_code}_{counter}"
                    counter += 1

                await Semester.create(
                    name=copy_name,
                    code=copy_code,
                    start_date=semester.start_date,
                    end_date=semester.end_date,
                    is_active=semester.is_active,
                    sort_order=semester.sort_order,
                    description=semester.description
                )
                success_count += 1
        except Exception as e:
            failed_count += 1
            failed_items.append({"id": semester_id, "error": str(e)})

    return BatchOperationResponse(
        success_count=success_count,
        failed_count=failed_count,
        total_count=len(request.get_ids()) * copy_count,
        message=f"批量复制完成：成功 {success_count} 个，失败 {failed_count} 个",
        failed_items=failed_items
    )

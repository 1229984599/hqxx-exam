from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from app.schemas.common import BatchUpdateRequest, BatchDeleteRequest, BatchCopyRequest, BatchOperationResponse
from app.models.admin import Admin
from app.models.role import Role, Permission, RolePermission, AdminRole, PermissionCode
from app.dependencies.auth import get_current_active_admin
from app.utils.permissions import PermissionManager, require_permission
from app.utils.logger import SystemLogger, LogModule

router = APIRouter(prefix="/roles", tags=["角色权限管理"])


class RoleResponse(BaseModel):
    id: int
    name: str
    code: str
    description: Optional[str]
    is_active: bool
    is_system: bool
    created_at: datetime
    permission_count: int = 0
    admin_count: int = 0

    class Config:
        from_attributes = True


class PermissionResponse(BaseModel):
    id: int
    name: str
    code: str
    resource: str
    action: str
    description: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True


class RoleCreateRequest(BaseModel):
    name: str
    code: str
    description: Optional[str] = None


class RoleUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class AssignRoleRequest(BaseModel):
    admin_id: int
    role_ids: List[int]


class AssignPermissionRequest(BaseModel):
    role_id: int
    permission_ids: List[int]


@router.get("/", response_model=List[RoleResponse], summary="获取角色列表")
async def get_roles(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    current_admin: Admin = Depends(get_current_active_admin)
):
    """获取角色列表"""
    # 检查权限
    if not await PermissionManager.has_permission(current_admin, PermissionCode.ADMINS_VIEW):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    query = Role.all()
    
    if search:
        query = query.filter(name__icontains=search)
    
    total = await query.count()
    offset = (page - 1) * size
    roles = await query.offset(offset).limit(size)
    
    # 获取每个角色的权限数量和管理员数量
    result = []
    for role in roles:
        permission_count = await RolePermission.filter(role=role).count()
        admin_count = await AdminRole.filter(role=role).count()
        
        role_data = RoleResponse.from_orm(role)
        role_data.permission_count = permission_count
        role_data.admin_count = admin_count
        result.append(role_data)
    
    return result


@router.post("/", response_model=RoleResponse, summary="创建角色")
async def create_role(
    role_data: RoleCreateRequest,
    current_admin: Admin = Depends(get_current_active_admin)
):
    """创建角色"""
    # 检查权限
    if not await PermissionManager.has_permission(current_admin, PermissionCode.ADMINS_CREATE):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    # 检查角色代码是否已存在
    existing_role = await Role.filter(code=role_data.code).first()
    if existing_role:
        raise HTTPException(status_code=400, detail="Role code already exists")
    
    # 创建角色
    role = await Role.create(
        name=role_data.name,
        code=role_data.code,
        description=role_data.description,
        created_by=current_admin.username
    )
    
    await SystemLogger.info(
        module=LogModule.SYSTEM,
        message=f"创建角色: {role.name}",
        details={"role_id": role.id, "role_code": role.code},
        user=current_admin.username
    )
    
    return RoleResponse.from_orm(role)


@router.put("/{role_id}", response_model=RoleResponse, summary="更新角色")
async def update_role(
    role_id: int,
    role_data: RoleUpdateRequest,
    current_admin: Admin = Depends(get_current_active_admin)
):
    """更新角色"""
    # 检查权限
    if not await PermissionManager.has_permission(current_admin, PermissionCode.ADMINS_EDIT):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    role = await Role.get_or_none(id=role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    # 系统角色不能修改
    if role.is_system:
        raise HTTPException(status_code=400, detail="Cannot modify system role")
    
    # 更新角色信息
    if role_data.name is not None:
        role.name = role_data.name
    if role_data.description is not None:
        role.description = role_data.description
    if role_data.is_active is not None:
        role.is_active = role_data.is_active
    
    await role.save()
    
    await SystemLogger.info(
        module=LogModule.SYSTEM,
        message=f"更新角色: {role.name}",
        details={"role_id": role.id, "changes": role_data.dict(exclude_unset=True)},
        user=current_admin.username
    )
    
    return RoleResponse.from_orm(role)


@router.delete("/{role_id}", summary="删除角色")
async def delete_role(
    role_id: int,
    current_admin: Admin = Depends(get_current_active_admin)
):
    """删除角色"""
    # 检查权限
    if not await PermissionManager.has_permission(current_admin, PermissionCode.ADMINS_DELETE):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    role = await Role.get_or_none(id=role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    # 系统角色不能删除
    if role.is_system:
        raise HTTPException(status_code=400, detail="Cannot delete system role")
    
    # 检查是否有管理员使用该角色
    admin_count = await AdminRole.filter(role=role).count()
    if admin_count > 0:
        raise HTTPException(status_code=400, detail="Cannot delete role with assigned admins")
    
    await role.delete()
    
    await SystemLogger.warning(
        module=LogModule.SYSTEM,
        message=f"删除角色: {role.name}",
        details={"role_id": role.id, "role_code": role.code},
        user=current_admin.username
    )
    
    return {"message": "Role deleted successfully"}


@router.get("/permissions", response_model=List[PermissionResponse], summary="获取权限列表")
async def get_permissions(
    current_admin: Admin = Depends(get_current_active_admin)
):
    """获取权限列表"""
    # 检查权限
    if not await PermissionManager.has_permission(current_admin, PermissionCode.ADMINS_VIEW):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    permissions = await Permission.filter(is_active=True).order_by("resource", "action")
    return [PermissionResponse.from_orm(perm) for perm in permissions]


@router.get("/{role_id}/permissions", response_model=List[PermissionResponse], summary="获取角色权限")
async def get_role_permissions(
    role_id: int,
    current_admin: Admin = Depends(get_current_active_admin)
):
    """获取角色的权限列表"""
    # 检查权限
    if not await PermissionManager.has_permission(current_admin, PermissionCode.ADMINS_VIEW):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    role = await Role.get_or_none(id=role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    permissions = await PermissionManager.get_role_permissions(role)
    return [PermissionResponse.from_orm(perm) for perm in permissions]


@router.post("/assign-permissions", summary="分配权限")
async def assign_permissions(
    request: AssignPermissionRequest,
    current_admin: Admin = Depends(get_current_active_admin)
):
    """为角色分配权限"""
    # 检查权限
    if not await PermissionManager.has_permission(current_admin, PermissionCode.ADMINS_EDIT):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    role = await Role.get_or_none(id=request.role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    # 清除现有权限
    await RolePermission.filter(role=role).delete()
    
    # 分配新权限
    assigned_count = 0
    for permission_id in request.permission_ids:
        permission = await Permission.get_or_none(id=permission_id)
        if permission and permission.is_active:
            await PermissionManager.assign_permission(role, permission, current_admin.username)
            assigned_count += 1
    
    await SystemLogger.info(
        module=LogModule.SYSTEM,
        message=f"为角色 {role.name} 分配权限",
        details={"role_id": role.id, "permission_count": assigned_count},
        user=current_admin.username
    )
    
    return {"message": f"Assigned {assigned_count} permissions to role"}


@router.post("/assign-roles", summary="分配角色")
async def assign_roles(
    request: AssignRoleRequest,
    current_admin: Admin = Depends(get_current_active_admin)
):
    """为管理员分配角色"""
    # 检查权限
    if not await PermissionManager.has_permission(current_admin, PermissionCode.ADMINS_EDIT):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    admin = await Admin.get_or_none(id=request.admin_id)
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    
    # 清除现有角色
    await AdminRole.filter(admin=admin).delete()
    
    # 分配新角色
    assigned_count = 0
    for role_id in request.role_ids:
        role = await Role.get_or_none(id=role_id)
        if role and role.is_active:
            await PermissionManager.assign_role(admin, role, current_admin.username)
            assigned_count += 1
    
    await SystemLogger.info(
        module=LogModule.SYSTEM,
        message=f"为管理员 {admin.username} 分配角色",
        details={"admin_id": admin.id, "role_count": assigned_count},
        user=current_admin.username
    )
    
    return {"message": f"Assigned {assigned_count} roles to admin"}


@router.post("/batch-update", response_model=BatchOperationResponse, summary="批量更新角色")
async def batch_update_roles(
    request: BatchUpdateRequest,
    current_admin: Admin = Depends(get_current_active_admin)
):
    """批量更新角色"""
    # 检查权限
    if not await PermissionManager.has_permission(current_admin, PermissionCode.ADMINS_EDIT):
        raise HTTPException(status_code=403, detail="Permission denied")

    success_count = 0
    failed_count = 0
    failed_items = []

    for role_id in request.get_ids():
        try:
            role = await Role.get_or_none(id=role_id)
            if not role:
                failed_count += 1
                failed_items.append({"id": role_id, "error": "Role not found"})
                continue

            # 系统角色不能修改
            if role.is_system:
                failed_count += 1
                failed_items.append({"id": role_id, "error": "Cannot modify system role"})
                continue

            # 更新角色数据
            for field, value in request.update_data.items():
                if hasattr(role, field) and field not in ['id', 'code', 'is_system', 'created_at', 'updated_at']:
                    setattr(role, field, value)

            await role.save()
            success_count += 1
        except Exception as e:
            failed_count += 1
            failed_items.append({"id": role_id, "error": str(e)})

    return BatchOperationResponse(
        success_count=success_count,
        failed_count=failed_count,
        total_count=len(request.get_ids()),
        message=f"批量更新完成：成功 {success_count} 个，失败 {failed_count} 个",
        failed_items=failed_items
    )


@router.post("/batch-delete", response_model=BatchOperationResponse, summary="批量删除角色")
async def batch_delete_roles(
    request: BatchDeleteRequest,
    current_admin: Admin = Depends(get_current_active_admin)
):
    """批量删除角色"""
    # 检查权限
    if not await PermissionManager.has_permission(current_admin, PermissionCode.ADMINS_DELETE):
        raise HTTPException(status_code=403, detail="Permission denied")

    success_count = 0
    failed_count = 0
    failed_items = []

    for role_id in request.get_ids():
        try:
            role = await Role.get_or_none(id=role_id)
            if not role:
                failed_count += 1
                failed_items.append({"id": role_id, "error": "Role not found"})
                continue

            # 系统角色不能删除
            if role.is_system:
                failed_count += 1
                failed_items.append({"id": role_id, "error": "Cannot delete system role"})
                continue

            # 检查是否有管理员使用该角色
            admin_count = await AdminRole.filter(role=role).count()
            if admin_count > 0:
                failed_count += 1
                failed_items.append({"id": role_id, "error": "Cannot delete role with assigned admins"})
                continue

            await role.delete()
            success_count += 1

            await SystemLogger.warning(
                module=LogModule.SYSTEM,
                message=f"批量删除角色: {role.name}",
                details={"role_id": role.id, "role_code": role.code},
                user=current_admin.username
            )
        except Exception as e:
            failed_count += 1
            failed_items.append({"id": role_id, "error": str(e)})

    return BatchOperationResponse(
        success_count=success_count,
        failed_count=failed_count,
        total_count=len(request.get_ids()),
        message=f"批量删除完成：成功 {success_count} 个，失败 {failed_count} 个",
        failed_items=failed_items
    )


@router.post("/batch-activate", response_model=BatchOperationResponse, summary="批量激活角色")
async def batch_activate_roles(
    request: BatchDeleteRequest,  # 使用BatchDeleteRequest因为只需要ids
    current_admin: Admin = Depends(get_current_active_admin)
):
    """批量激活角色"""
    # 检查权限
    if not await PermissionManager.has_permission(current_admin, PermissionCode.ADMINS_EDIT):
        raise HTTPException(status_code=403, detail="Permission denied")

    success_count = 0
    failed_count = 0
    failed_items = []

    for role_id in request.get_ids():
        try:
            role = await Role.get_or_none(id=role_id)
            if not role:
                failed_count += 1
                failed_items.append({"id": role_id, "error": "Role not found"})
                continue

            role.is_active = True
            await role.save()
            success_count += 1
        except Exception as e:
            failed_count += 1
            failed_items.append({"id": role_id, "error": str(e)})

    return BatchOperationResponse(
        success_count=success_count,
        failed_count=failed_count,
        total_count=len(request.get_ids()),
        message=f"批量激活完成：成功 {success_count} 个，失败 {failed_count} 个",
        failed_items=failed_items
    )


@router.post("/batch-deactivate", response_model=BatchOperationResponse, summary="批量禁用角色")
async def batch_deactivate_roles(
    request: BatchDeleteRequest,
    current_admin: Admin = Depends(get_current_active_admin)
):
    """批量禁用角色"""
    # 检查权限
    if not await PermissionManager.has_permission(current_admin, PermissionCode.ADMINS_EDIT):
        raise HTTPException(status_code=403, detail="Permission denied")

    success_count = 0
    failed_count = 0
    failed_items = []

    for role_id in request.get_ids():
        try:
            role = await Role.get_or_none(id=role_id)
            if not role:
                failed_count += 1
                failed_items.append({"id": role_id, "error": "Role not found"})
                continue

            # 系统角色不能禁用
            if role.is_system:
                failed_count += 1
                failed_items.append({"id": role_id, "error": "Cannot deactivate system role"})
                continue

            role.is_active = False
            await role.save()
            success_count += 1
        except Exception as e:
            failed_count += 1
            failed_items.append({"id": role_id, "error": str(e)})

    return BatchOperationResponse(
        success_count=success_count,
        failed_count=failed_count,
        total_count=len(request.get_ids()),
        message=f"批量禁用完成：成功 {success_count} 个，失败 {failed_count} 个",
        failed_items=failed_items
    )


class BatchAssignPermissionRequest(BaseModel):
    role_ids: List[int]
    permission_codes: List[str]


@router.post("/batch-assign-permissions", response_model=BatchOperationResponse, summary="批量分配权限")
async def batch_assign_permissions(
    request: BatchAssignPermissionRequest,
    current_admin: Admin = Depends(get_current_active_admin)
):
    """批量为角色分配权限"""
    # 检查权限
    if not await PermissionManager.has_permission(current_admin, PermissionCode.ADMINS_EDIT):
        raise HTTPException(status_code=403, detail="Permission denied")

    success_count = 0
    failed_count = 0
    failed_items = []

    for role_id in request.role_ids:
        try:
            role = await Role.get_or_none(id=role_id)
            if not role:
                failed_count += 1
                failed_items.append({"id": role_id, "error": "Role not found"})
                continue

            # 系统角色不能修改权限
            if role.is_system:
                failed_count += 1
                failed_items.append({"id": role_id, "error": "Cannot modify system role permissions"})
                continue

            # 清除现有权限
            await RolePermission.filter(role=role).delete()

            # 分配新权限
            assigned_count = 0
            for permission_code in request.permission_codes:
                permission = await Permission.filter(code=permission_code, is_active=True).first()
                if permission:
                    await PermissionManager.assign_permission(role, permission, current_admin.username)
                    assigned_count += 1

            success_count += 1

            await SystemLogger.info(
                module=LogModule.SYSTEM,
                message=f"批量为角色 {role.name} 分配权限",
                details={"role_id": role.id, "permission_count": assigned_count},
                user=current_admin.username
            )
        except Exception as e:
            failed_count += 1
            failed_items.append({"id": role_id, "error": str(e)})

    return BatchOperationResponse(
        success_count=success_count,
        failed_count=failed_count,
        total_count=len(request.role_ids),
        message=f"批量权限分配完成：成功 {success_count} 个，失败 {failed_count} 个",
        failed_items=failed_items
    )

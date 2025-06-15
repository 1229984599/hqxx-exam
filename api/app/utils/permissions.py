from typing import List, Optional
from fastapi import HTTPException, status
from app.models.admin import Admin
from app.models.role import Role, Permission, RolePermission, AdminRole, PermissionCode


class PermissionManager:
    """权限管理器"""
    
    @staticmethod
    async def get_admin_permissions(admin: Admin) -> List[str]:
        """获取管理员的所有权限"""
        # 超级管理员拥有所有权限
        if admin.is_superuser:
            return ["*"]  # 通配符表示所有权限
        
        # 获取管理员的角色
        admin_roles = await AdminRole.filter(admin=admin).prefetch_related("role")
        
        if not admin_roles:
            return []
        
        # 获取所有角色的权限
        permissions = set()
        for admin_role in admin_roles:
            role = admin_role.role
            if role.is_active:
                role_permissions = await RolePermission.filter(
                    role=role
                ).prefetch_related("permission")
                
                for rp in role_permissions:
                    if rp.permission.is_active:
                        permissions.add(rp.permission.code)
        
        return list(permissions)
    
    @staticmethod
    async def has_permission(admin: Admin, permission_code: str) -> bool:
        """检查管理员是否有指定权限"""
        # 超级管理员拥有所有权限
        if admin.is_superuser:
            return True
        
        permissions = await PermissionManager.get_admin_permissions(admin)
        return permission_code in permissions or "*" in permissions
    
    @staticmethod
    async def has_any_permission(admin: Admin, permission_codes: List[str]) -> bool:
        """检查管理员是否有任意一个权限"""
        if admin.is_superuser:
            return True
        
        permissions = await PermissionManager.get_admin_permissions(admin)
        if "*" in permissions:
            return True
        
        return any(code in permissions for code in permission_codes)
    
    @staticmethod
    async def has_all_permissions(admin: Admin, permission_codes: List[str]) -> bool:
        """检查管理员是否有所有权限"""
        if admin.is_superuser:
            return True
        
        permissions = await PermissionManager.get_admin_permissions(admin)
        if "*" in permissions:
            return True
        
        return all(code in permissions for code in permission_codes)
    
    @staticmethod
    async def get_admin_roles(admin: Admin) -> List[Role]:
        """获取管理员的角色列表"""
        admin_roles = await AdminRole.filter(admin=admin).prefetch_related("role")
        return [ar.role for ar in admin_roles if ar.role.is_active]

    @staticmethod
    async def has_role(admin: Admin, role_code: str) -> bool:
        """检查管理员是否有指定角色"""
        # 超级管理员拥有所有角色
        if admin.is_superuser:
            return True

        roles = await PermissionManager.get_admin_roles(admin)
        return any(role.code == role_code for role in roles)

    @staticmethod
    async def has_any_role(admin: Admin, role_codes: List[str]) -> bool:
        """检查管理员是否有任意一个角色"""
        if admin.is_superuser:
            return True

        roles = await PermissionManager.get_admin_roles(admin)
        admin_role_codes = [role.code for role in roles]
        return any(code in admin_role_codes for code in role_codes)

    @staticmethod
    async def has_all_roles(admin: Admin, role_codes: List[str]) -> bool:
        """检查管理员是否有所有角色"""
        if admin.is_superuser:
            return True

        roles = await PermissionManager.get_admin_roles(admin)
        admin_role_codes = [role.code for role in roles]
        return all(code in admin_role_codes for code in role_codes)
    
    @staticmethod
    async def assign_role(admin: Admin, role: Role, created_by: str = None) -> bool:
        """为管理员分配角色"""
        try:
            # 检查是否已经有该角色
            existing = await AdminRole.filter(admin=admin, role=role).first()
            if existing:
                return False
            
            # 创建角色分配
            await AdminRole.create(
                admin=admin,
                role=role,
                created_by=created_by
            )
            return True
        except Exception:
            return False
    
    @staticmethod
    async def remove_role(admin: Admin, role: Role) -> bool:
        """移除管理员的角色"""
        try:
            admin_role = await AdminRole.filter(admin=admin, role=role).first()
            if admin_role:
                await admin_role.delete()
                return True
            return False
        except Exception:
            return False
    
    @staticmethod
    async def get_role_permissions(role: Role) -> List[Permission]:
        """获取角色的权限列表"""
        role_permissions = await RolePermission.filter(role=role).prefetch_related("permission")
        return [rp.permission for rp in role_permissions if rp.permission.is_active]
    
    @staticmethod
    async def assign_permission(role: Role, permission: Permission, created_by: str = None) -> bool:
        """为角色分配权限"""
        try:
            # 检查是否已经有该权限
            existing = await RolePermission.filter(role=role, permission=permission).first()
            if existing:
                return False
            
            # 创建权限分配
            await RolePermission.create(
                role=role,
                permission=permission,
                created_by=created_by
            )
            return True
        except Exception:
            return False
    
    @staticmethod
    async def remove_permission(role: Role, permission: Permission) -> bool:
        """移除角色的权限"""
        try:
            role_permission = await RolePermission.filter(role=role, permission=permission).first()
            if role_permission:
                await role_permission.delete()
                return True
            return False
        except Exception:
            return False


def require_permission(permission_code: str):
    """权限验证装饰器"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # 从kwargs中获取current_admin
            current_admin = kwargs.get('current_admin')
            if not current_admin:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            # 检查权限
            has_perm = await PermissionManager.has_permission(current_admin, permission_code)
            if not has_perm:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied: {permission_code}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_any_permission(permission_codes: List[str]):
    """任意权限验证装饰器"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            current_admin = kwargs.get('current_admin')
            if not current_admin:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            has_perm = await PermissionManager.has_any_permission(current_admin, permission_codes)
            if not has_perm:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied: requires any of {permission_codes}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_all_permissions(permission_codes: List[str]):
    """所有权限验证装饰器"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            current_admin = kwargs.get('current_admin')
            if not current_admin:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )

            has_perm = await PermissionManager.has_all_permissions(current_admin, permission_codes)
            if not has_perm:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied: requires all of {permission_codes}"
                )

            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_role(role_code: str):
    """角色验证装饰器（RBAC核心）"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            current_admin = kwargs.get('current_admin')
            if not current_admin:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )

            has_role = await PermissionManager.has_role(current_admin, role_code)
            if not has_role:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Role required: {role_code}"
                )

            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_any_role(role_codes: List[str]):
    """任意角色验证装饰器"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            current_admin = kwargs.get('current_admin')
            if not current_admin:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )

            has_role = await PermissionManager.has_any_role(current_admin, role_codes)
            if not has_role:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Role required: any of {role_codes}"
                )

            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_all_roles(role_codes: List[str]):
    """所有角色验证装饰器"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            current_admin = kwargs.get('current_admin')
            if not current_admin:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )

            has_role = await PermissionManager.has_all_roles(current_admin, role_codes)
            if not has_role:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Role required: all of {role_codes}"
                )

            return await func(*args, **kwargs)
        return wrapper
    return decorator

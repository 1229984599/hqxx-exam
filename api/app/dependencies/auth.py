from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.models.admin import Admin
from app.utils.auth import verify_token

security = HTTPBearer()


async def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Admin:
    """获取当前管理员"""
    # 检查是否提供了token
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供访问令牌，请先登录",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    payload = verify_token(token)

    # token无效或已过期
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="访问令牌无效或已过期，请重新登录",
            headers={"WWW-Authenticate": "Bearer"},
        )

    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="访问令牌格式错误，请重新登录",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 查找用户（包括非激活用户）
    admin = await Admin.filter(username=username).first()
    if admin is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在，请重新登录",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 检查用户是否被禁用
    if not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账户已被禁用，请联系系统管理员",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return admin


async def get_current_active_admin(
    current_admin: Admin = Depends(get_current_admin)
) -> Admin:
    """获取当前激活的管理员"""
    # 这个检查实际上在get_current_admin中已经做了，这里保留作为双重保险
    if not current_admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账户已被禁用，请联系系统管理员"
        )
    return current_admin


async def get_current_superuser(
    current_admin: Admin = Depends(get_current_admin)
) -> Admin:
    """获取当前超级管理员"""
    if not current_admin.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，此操作需要超级管理员权限"
        )
    return current_admin

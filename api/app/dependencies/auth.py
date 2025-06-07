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
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        raise credentials_exception
    
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    
    admin = await Admin.filter(username=username, is_active=True).first()
    if admin is None:
        raise credentials_exception
    
    return admin


async def get_current_active_admin(
    current_admin: Admin = Depends(get_current_admin)
) -> Admin:
    """获取当前激活的管理员"""
    if not current_admin.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_admin


async def get_current_superuser(
    current_admin: Admin = Depends(get_current_admin)
) -> Admin:
    """获取当前超级管理员"""
    if not current_admin.is_superuser:
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_admin

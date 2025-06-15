from pydantic import BaseModel, EmailStr
from typing import Optional, List


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class AdminLogin(BaseModel):
    username: str
    password: str


class AdminCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    is_superuser: bool = False


class AdminUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None


class AdminResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None
    is_active: bool
    is_superuser: bool

    class Config:
        from_attributes = True


class RoleInfo(BaseModel):
    """角色信息"""
    id: int
    name: str
    code: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class AdminPermissionsResponse(BaseModel):
    """管理员权限响应"""
    permissions: List[str]
    roles: List[RoleInfo]
    is_superuser: bool

    class Config:
        from_attributes = True

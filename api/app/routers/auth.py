from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.models.admin import Admin
from app.schemas.auth import Token, AdminLogin, AdminCreate, AdminResponse
from app.utils.auth import verify_password, get_password_hash, create_access_token
from app.dependencies.auth import get_current_active_admin, get_current_superuser
from app.config import settings

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/login", response_model=Token, summary="管理员登录")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """管理员登录"""
    admin = await Admin.filter(username=form_data.username, is_active=True).first()
    
    if not admin or not verify_password(form_data.password, admin.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": admin.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login/json", response_model=Token, summary="JSON格式登录")
async def login_json(login_data: AdminLogin):
    """JSON格式的管理员登录"""
    admin = await Admin.filter(username=login_data.username, is_active=True).first()
    
    if not admin or not verify_password(login_data.password, admin.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": admin.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=AdminResponse, summary="获取当前用户信息")
async def read_users_me(current_admin: Admin = Depends(get_current_active_admin)):
    """获取当前登录的管理员信息"""
    return current_admin


@router.post("/register", response_model=AdminResponse, summary="注册管理员")
async def register_admin(
    admin_data: AdminCreate,
    current_admin: Admin = Depends(get_current_superuser)
):
    """注册新管理员（仅超级管理员可操作）"""
    # 检查用户名是否已存在
    existing_admin = await Admin.filter(username=admin_data.username).first()
    if existing_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # 检查邮箱是否已存在
    existing_email = await Admin.filter(email=admin_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # 创建新管理员
    hashed_password = get_password_hash(admin_data.password)
    admin = await Admin.create(
        username=admin_data.username,
        email=admin_data.email,
        hashed_password=hashed_password,
        full_name=admin_data.full_name,
        is_superuser=admin_data.is_superuser
    )
    
    return admin

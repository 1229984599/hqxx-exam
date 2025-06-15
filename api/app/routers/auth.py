from datetime import timedelta, datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordRequestForm
from app.models.admin import Admin
from app.models.question import Question
from app.models.system_log import SystemLog, LogLevel
from app.schemas.auth import Token, AdminLogin, AdminCreate, AdminResponse, AdminUpdate, AdminPermissionsResponse, RoleInfo
from app.utils.auth import verify_password, get_password_hash, create_access_token, verify_token_with_detail
from app.dependencies.auth import get_current_active_admin, get_current_superuser
from app.config import settings
from app.utils.logger import SystemLogger
from app.utils.permissions import PermissionManager

router = APIRouter(prefix="/auth", tags=["认证"])


class UserStatsResponse(BaseModel):
    """用户统计响应模型"""
    created_questions: int
    last_login_days: int
    total_login_count: int
    join_days: int


@router.post("/login", response_model=Token, summary="管理员登录")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), request: Request = None):
    """管理员登录"""
    # 检查用户名是否为空
    if not form_data.username or not form_data.username.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名不能为空",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 检查密码是否为空
    if not form_data.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码不能为空",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 查找用户（包括非激活用户）
    admin = await Admin.filter(username=form_data.username.strip()).first()

    # 用户不存在
    if not admin:
        await SystemLogger.auth_login(form_data.username.strip(), False, request)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名不存在，请检查用户名是否正确",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 用户被禁用
    if not admin.is_active:
        await SystemLogger.auth_login(admin.username, False, request)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账户已被禁用，请联系系统管理员",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 密码错误
    if not verify_password(form_data.password, admin.hashed_password):
        await SystemLogger.auth_login(admin.username, False, request)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="密码错误，请检查密码是否正确",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 登录成功，生成token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": admin.username}, expires_delta=access_token_expires
    )

    # 记录登录成功日志
    await SystemLogger.auth_login(admin.username, True, request)

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login/json", response_model=Token, summary="JSON格式登录")
async def login_json(login_data: AdminLogin, request: Request = None):
    """JSON格式的管理员登录"""
    # 检查用户名是否为空
    if not login_data.username or not login_data.username.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名不能为空"
        )

    # 检查密码是否为空
    if not login_data.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码不能为空"
        )

    # 查找用户（包括非激活用户）
    admin = await Admin.filter(username=login_data.username.strip()).first()

    # 用户不存在
    if not admin:
        await SystemLogger.auth_login(login_data.username.strip(), False, request)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名不存在，请检查用户名是否正确"
        )

    # 用户被禁用
    if not admin.is_active:
        await SystemLogger.auth_login(admin.username, False, request)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账户已被禁用，请联系系统管理员"
        )

    # 密码错误
    if not verify_password(login_data.password, admin.hashed_password):
        await SystemLogger.auth_login(admin.username, False, request)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="密码错误，请检查密码是否正确"
        )

    # 登录成功，生成token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": admin.username}, expires_delta=access_token_expires
    )

    # 记录登录成功日志
    await SystemLogger.auth_login(admin.username, True, request)

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/refresh", response_model=Token, summary="刷新访问令牌")
async def refresh_token(current_admin: Admin = Depends(get_current_active_admin)):
    """刷新访问令牌"""
    try:
        # 生成新的访问令牌
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": current_admin.username},
            expires_delta=access_token_expires
        )

        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"刷新令牌失败：{str(e)}"
        )


@router.get("/me", response_model=AdminResponse, summary="获取当前用户信息")
async def read_users_me(current_admin: Admin = Depends(get_current_active_admin)):
    """获取当前登录的管理员信息"""
    return current_admin


@router.get("/profile/stats", response_model=UserStatsResponse, summary="获取用户统计信息")
async def get_user_stats(current_admin: Admin = Depends(get_current_active_admin)):
    """获取当前用户的统计信息"""
    # 获取用户创建的试题数量
    created_questions = await Question.filter(created_by=current_admin.username).count()

    # 获取用户登录次数（从系统日志中统计）
    total_login_count = await SystemLog.filter(
        module="auth",
        message__icontains="登录成功",
        user=current_admin.username
    ).count()

    # 计算最后登录时间（天数）
    last_login_log = await SystemLog.filter(
        module="auth",
        message__icontains="登录成功",
        user=current_admin.username
    ).order_by("-timestamp").first()

    last_login_days = 0
    if last_login_log:
        days_diff = (datetime.now() - last_login_log.timestamp).days
        last_login_days = max(0, days_diff)

    # 计算加入天数
    join_days = (datetime.now() - current_admin.created_at).days

    return UserStatsResponse(
        created_questions=created_questions,
        last_login_days=last_login_days,
        total_login_count=total_login_count,
        join_days=join_days
    )


@router.get("/permissions", response_model=AdminPermissionsResponse, summary="获取当前用户权限")
async def get_current_user_permissions(current_admin: Admin = Depends(get_current_active_admin)):
    """获取当前登录管理员的权限和角色信息"""
    # 获取用户权限
    permissions = await PermissionManager.get_admin_permissions(current_admin)

    # 获取用户角色
    roles = await PermissionManager.get_admin_roles(current_admin)
    role_info = [
        RoleInfo(
            id=role.id,
            name=role.name,
            code=role.code,
            description=role.description
        ) for role in roles
    ]

    return AdminPermissionsResponse(
        permissions=permissions,
        roles=role_info,
        is_superuser=current_admin.is_superuser
    )


@router.post("/register", response_model=AdminResponse, summary="注册管理员")
async def register_admin(
    admin_data: AdminCreate,
    current_admin: Admin = Depends(get_current_superuser)
):
    """注册新管理员（仅超级管理员可操作）"""
    # 验证输入数据
    if not admin_data.username or not admin_data.username.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名不能为空"
        )

    if not admin_data.password or len(admin_data.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码不能为空且长度不能少于6位"
        )

    if not admin_data.email or not admin_data.email.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱不能为空"
        )

    # 检查用户名是否已存在
    existing_admin = await Admin.filter(username=admin_data.username.strip()).first()
    if existing_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"用户名 '{admin_data.username}' 已被注册，请选择其他用户名"
        )

    # 检查邮箱是否已存在
    existing_email = await Admin.filter(email=admin_data.email.strip().lower()).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"邮箱 '{admin_data.email}' 已被注册，请使用其他邮箱"
        )

    try:
        # 创建新管理员
        hashed_password = get_password_hash(admin_data.password)
        admin = await Admin.create(
            username=admin_data.username.strip(),
            email=admin_data.email.strip().lower(),
            hashed_password=hashed_password,
            full_name=admin_data.full_name.strip() if admin_data.full_name else None,
            is_superuser=admin_data.is_superuser
        )

        return admin
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建管理员账户失败：{str(e)}"
        )


@router.put("/profile", response_model=AdminResponse, summary="更新个人资料")
async def update_profile(
    profile_data: AdminUpdate,
    current_admin: Admin = Depends(get_current_active_admin)
):
    """更新当前用户的个人资料"""
    try:
        # 检查邮箱是否已被其他用户使用
        if profile_data.email and profile_data.email.strip():
            existing_email = await Admin.filter(
                email=profile_data.email.strip().lower()
            ).exclude(id=current_admin.id).first()

            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"邮箱 '{profile_data.email}' 已被其他用户使用"
                )

        # 更新用户信息
        update_data = {}
        if profile_data.email is not None:
            update_data['email'] = profile_data.email.strip().lower()
        if profile_data.full_name is not None:
            update_data['full_name'] = profile_data.full_name.strip() if profile_data.full_name else None
        if profile_data.phone is not None:
            update_data['phone'] = profile_data.phone.strip() if profile_data.phone else None
        if profile_data.avatar is not None:
            update_data['avatar'] = profile_data.avatar

        if update_data:
            await Admin.filter(id=current_admin.id).update(**update_data)
            # 重新获取更新后的用户信息
            updated_admin = await Admin.get(id=current_admin.id)
            return updated_admin

        return current_admin

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新个人资料失败：{str(e)}"
        )

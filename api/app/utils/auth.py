from datetime import datetime, timedelta
from typing import Optional, Tuple
from jose import JWTError, jwt, ExpiredSignatureError
from passlib.context import CryptContext
from app.config import settings

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """获取密码哈希"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """验证令牌"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except ExpiredSignatureError:
        # Token已过期
        return None
    except JWTError:
        # Token格式错误或签名无效
        return None


def verify_token_with_detail(token: str) -> Tuple[Optional[dict], str]:
    """验证令牌并返回详细错误信息"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload, ""
    except ExpiredSignatureError:
        return None, "访问令牌已过期，请重新登录"
    except JWTError as e:
        if "Invalid token" in str(e):
            return None, "访问令牌格式错误"
        elif "Invalid signature" in str(e):
            return None, "访问令牌签名无效"
        else:
            return None, "访问令牌验证失败"
    except Exception as e:
        return None, f"令牌验证时发生未知错误：{str(e)}"


def get_token_expiry_time(token: str) -> Optional[datetime]:
    """获取token的过期时间"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        exp_timestamp = payload.get("exp")
        if exp_timestamp:
            return datetime.fromtimestamp(exp_timestamp)
        return None
    except:
        return None


def is_token_expiring_soon(token: str, threshold_minutes: int = 5) -> bool:
    """检查token是否即将过期（默认5分钟内）"""
    try:
        expiry_time = get_token_expiry_time(token)
        if not expiry_time:
            return True  # 无法获取过期时间，认为需要刷新

        current_time = datetime.utcnow()
        time_until_expiry = expiry_time - current_time

        return time_until_expiry.total_seconds() <= (threshold_minutes * 60)
    except:
        return True  # 出错时认为需要刷新

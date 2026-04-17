"""
认证服务 - 处理用户认证相关逻辑
"""

from datetime import datetime, timedelta
from typing import Optional
import re

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

import config
from app.database import get_db, UserRepository

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer Token
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    """哈希密码"""
    return pwd_context.hash(password)


def validate_email(email: str) -> bool:
    """验证邮箱格式"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password_strength(password: str) -> tuple:
    """
    验证密码强度
    返回: (is_valid, message)
    """
    if len(password) < 8:
        return False, "密码长度至少8位"
    return True, ""


def create_access_token(data: dict, remember_me: bool = False) -> str:
    """
    创建JWT访问令牌
    
    Args:
        data: 包含用户信息的数据字典
        remember_me: 是否延长有效期（记住我）
    
    Returns:
        JWT token字符串
    """
    to_encode = data.copy()
    
    # 设置过期时间
    if remember_me:
        expire = datetime.utcnow() + timedelta(minutes=config.JWT_REMEMBER_EXPIRE_MINUTES)
    else:
        expire = datetime.utcnow() + timedelta(minutes=config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode,
        config.JWT_SECRET_KEY,
        algorithm=config.JWT_ALGORITHM
    )
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    解码JWT令牌
    
    Args:
        token: JWT token字符串
    
    Returns:
        解码后的数据字典，如果失败返回None
    """
    try:
        payload = jwt.decode(
            token,
            config.JWT_SECRET_KEY,
            algorithms=[config.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    验证Token的依赖项
    
    用于保护需要登录的API路由
    """
    token = credentials.credentials
    
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token已过期或无效",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 检查用户ID
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的Token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload


def get_current_user(
    payload: dict = Depends(verify_token),
    db: Session = Depends(get_db)
) -> dict:
    """
    获取当前登录用户
    
    返回用户信息字典
    """
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的用户信息"
        )
    
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(int(user_id))
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账户已被禁用"
        )
    
    # Check admin status: database field OR whitelist
    import config
    is_admin = user.is_admin or config.is_email_whitelisted(user.email)
    
    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "is_admin": is_admin,
        "is_subscribed": user.is_subscribed,
        "subscription_status": user.subscription_status,
        "subscription_end_date": user.subscription_end_date.isoformat() if user.subscription_end_date else None,
        "is_whitelisted": user.is_whitelisted
    }


class AuthService:
    """认证服务类"""
    
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
    
    def register(self, email: str, password: str, username: str = None) -> tuple:
        """
        用户注册
        
        Returns:
            (success, message, user_data)
        """
        # 验证邮箱格式
        if not validate_email(email):
            return False, "邮箱格式不正确", None
        
        # 验证密码强度
        is_valid, msg = validate_password_strength(password)
        if not is_valid:
            return False, msg, None
        
        # 检查邮箱是否已注册
        if self.user_repo.email_exists(email):
            return False, "该邮箱已被注册", None
        
        # 创建用户
        password_hash = hash_password(password)
        user = self.user_repo.create(
            email=email.lower(),
            password_hash=password_hash,
            username=username
        )
        
        return True, "注册成功", {
            "id": user.id,
            "email": user.email,
            "username": user.username
        }
    
    def login(self, email: str, password: str, remember_me: bool = False) -> tuple:
        """
        用户登录
        
        Returns:
            (success, message, token/user_data)
        """
        # 获取用户
        user = self.user_repo.get_by_email(email)
        
        if user is None:
            # 为防止邮箱枚举攻击，不暴露邮箱是否存在
            return False, "邮箱或密码错误", None
        
        # 验证密码
        if not verify_password(password, user.password_hash):
            return False, "邮箱或密码错误", None
        
        # 检查账户状态
        if not user.is_active:
            return False, "账户已被禁用，请联系管理员", None
        
        # 更新最后登录时间
        self.user_repo.update_last_login(user.id)
        
        # 生成Token
        token = create_access_token(
            data={"sub": str(user.id), "email": user.email},
            remember_me=remember_me
        )
        
        return True, "登录成功", {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username
            }
        }
    
    def get_user_info(self, user_id: int) -> Optional[dict]:
        """获取用户信息"""
        user = self.user_repo.get_by_id(user_id)
        if user:
            return {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "created_at": user.created_at.isoformat() if user.created_at else None
            }
        return None
    
    def change_password(self, user_id: int, old_password: str, new_password: str) -> tuple:
        """
        修改密码
        
        Returns:
            (success, message)
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return False, "用户不存在"
        
        # 验证旧密码
        if not verify_password(old_password, user.password_hash):
            return False, "旧密码不正确"
        
        # 验证新密码强度
        is_valid, msg = validate_password_strength(new_password)
        if not is_valid:
            return False, msg
        
        # 检查新旧密码是否相同
        if verify_password(new_password, user.password_hash):
            return False, "新密码不能与旧密码相同"
        
        # 更新密码
        self.user_repo.update_password(user_id, hash_password(new_password))
        
        return True, "密码修改成功"
    
    def update_username(self, user_id: int, new_username: str) -> tuple:
        """
        修改用户名
        
        Returns:
            (success, message)
        """
        if not new_username or len(new_username) < 2:
            return False, "用户名长度至少2位"
        
        if len(new_username) > 50:
            return False, "用户名长度不能超过50位"
        
        self.user_repo.update_username(user_id, new_username)
        
        return True, "用户名修改成功"
    
    def generate_reset_token(self, email: str) -> tuple:
        """
        生成密码重置令牌
        
        Returns:
            (success, message, token)
        """
        # 验证邮箱格式
        if not validate_email(email):
            return False, "邮箱格式不正确", None
        
        # 检查用户是否存在
        user = self.user_repo.get_by_email(email)
        if user is None:
            # 为防止邮箱枚举攻击，总是返回成功
            return True, "如果该邮箱已注册，重置链接已发送至您的邮箱", None
        
        # 生成随机令牌
        import secrets
        token = secrets.token_urlsafe(32)
        
        # 设置过期时间（1小时）
        expires_at = datetime.utcnow() + timedelta(hours=1)
        
        # 保存令牌到数据库
        self.user_repo.set_reset_token(email, token, expires_at)
        
        return True, "重置链接已生成", token
    
    def reset_password_with_token(self, token: str, new_password: str) -> tuple:
        """
        使用令牌重置密码
        
        Returns:
            (success, message)
        """
        # 验证新密码强度
        is_valid, msg = validate_password_strength(new_password)
        if not is_valid:
            return False, msg
        
        # 使用仓储类重置密码
        return self.user_repo.reset_password(token, hash_password(new_password))

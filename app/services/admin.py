"""
管理员服务 - 提供管理员权限检查功能
"""

from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session

from app.database import get_db, UserRepository
from app.services.auth import get_current_user

# 白名单邮箱列表 - 这些用户视为管理员
ADMIN_WHITELIST_EMAILS = [
    "whitelist@imvu-analytics.com",
    "nlfd8910@gmail.com"
]


def is_admin_whitelisted(email: str) -> bool:
    """检查用户是否在管理员白名单中"""
    return email.lower() in [e.lower() for e in ADMIN_WHITELIST_EMAILS]


async def require_admin(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """
    管理员权限检查依赖项
    
    用于保护只有管理员才能访问的API路由
    
    管理员判断逻辑：
    1. 用户 is_admin = True
    2. 用户邮箱在白名单中
    """
    user_email = current_user.get("email")
    user_id = current_user.get("id")
    
    # 获取完整用户信息检查 is_admin 字段
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=404,
            detail="用户不存在"
        )
    
    # 检查是否是管理员
    is_admin = user.is_admin or is_admin_whitelisted(user_email)
    
    if not is_admin:
        raise HTTPException(
            status_code=403,
            detail="需要管理员权限才能访问此功能"
        )
    
    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "is_admin": True
    }

"""
订阅检查服务 - 检查用户是否有有效订阅
"""

from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session

from app.database import get_db, UserRepository
from app.services.auth import get_current_user

# 白名单邮箱列表 - 这些用户跳过订阅检查
WHITELIST_EMAILS = [
    "whitelist@imvu-analytics.com",
    "nlfd8910@gmail.com"
]


def is_whitelisted(email: str) -> bool:
    """检查用户是否在白名单中"""
    return email.lower() in [e.lower() for e in WHITELIST_EMAILS]


def has_active_subscription(db: Session, user_id: int) -> bool:
    """
    检查用户是否有有效的订阅
    
    Returns:
        True: 有订阅或在白名单中
        False: 无订阅
    """
    from app.models import User
    from datetime import datetime
    
    # 获取用户信息
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        return False
    
    # 白名单用户跳过检查
    if is_whitelisted(user.email):
        return True
    
    # 检查订阅状态
    if user.subscription_status == 'active':
        # 检查订阅是否过期
        if user.subscription_end_date:
            if user.subscription_end_date > datetime.utcnow():
                return True
        else:
            # 没有过期时间，认为订阅有效
            return True
    
    return False


async def require_subscription(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """
    订阅检查依赖项
    
    用于保护需要订阅才能使用的API路由
    """
    user_email = current_user.get("email")
    user_id = current_user.get("id")
    
    # 白名单用户跳过检查
    if is_whitelisted(user_email):
        return current_user
    
    # 检查订阅状态
    if not has_active_subscription(db, user_id):
        raise HTTPException(
            status_code=403,
            detail="需要订阅才能使用此功能。请前往订阅页面升级您的账户。"
        )
    
    return current_user

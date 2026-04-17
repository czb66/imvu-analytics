"""
订阅检查服务 - 检查用户是否有有效订阅
"""

from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session

from app.database import get_db, UserRepository
from app.services.auth import get_current_user
import config  # 使用统一的配置管理


def is_whitelisted(email: str, db: Session = None) -> bool:
    """
    检查用户是否在白名单中
    
    同时检查：
    1. 配置文件中的白名单列表
    2. 数据库中的 is_whitelisted 字段
    """
    # 检查配置文件白名单
    if config.is_email_whitelisted(email):
        return True
    
    # 检查数据库白名单字段
    if db:
        from app.models import User
        user = db.query(User).filter(User.email == email).first()
        if user and user.is_whitelisted:
            return True
    
    return False


def has_active_subscription(db: Session, user_id: int) -> bool:
    """
    检查用户是否有有效的订阅或试用期
    
    Returns:
        True: 有订阅/试用期或在白名单中
        False: 无订阅且试用期已过
    """
    from app.models import User
    from datetime import datetime
    
    # 获取用户信息
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        return False
    
    # 白名单用户跳过检查
    if is_whitelisted(user.email, db):
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
    
    # 检查试用期
    if user.trial_end_date and user.trial_end_date > datetime.utcnow():
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
    if is_whitelisted(user_email, db):
        return current_user
    
    # 检查订阅状态
    if not has_active_subscription(db, user_id):
        raise HTTPException(
            status_code=403,
            detail="需要订阅才能使用此功能。请前往订阅页面升级您的账户。"
        )
    
    return current_user

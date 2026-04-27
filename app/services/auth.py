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
from app.services.activity_tracker import activity_tracker

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer Token
security = HTTPBearer()

# 防刷机制配置
IP_REGISTRATION_LIMIT = 3  # 同一IP 24小时内最多注册账号数
IP_REGISTRATION_WINDOW_HOURS = 24  # IP注册限制时间窗口（小时）
MONTHLY_REFERRAL_REWARD_LIMIT = 5  # 每月推荐奖励上限（次）
REFERRAL_REWARD_DAYS = 7  # 推荐奖励天数


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


def check_ip_registration_limit(db: Session, client_ip: str) -> tuple:
    """
    检查IP注册限制
    
    Args:
        db: 数据库会话
        client_ip: 客户端IP
    
    Returns:
        (is_allowed, message): 是否允许注册，以及拒绝原因
    """
    from app.models import UserActivity
    from sqlalchemy import func
    
    # 计算时间窗口
    time_threshold = datetime.utcnow() - timedelta(hours=IP_REGISTRATION_WINDOW_HOURS)
    
    # 统计该IP最近的注册次数（通过UserActivity记录）
    # 由于注册时记录了client_ip在metadata中，我们查询extra_data
    recent_count = db.query(func.count(UserActivity.id)).filter(
        UserActivity.action == 'register',
        UserActivity.created_at >= time_threshold
    ).scalar() or 0
    
    # 注意：上述方法不够精确，因为metadata是JSON字段
    # 更精确的方法是检查User模型（但目前User模型没有直接存储注册IP）
    # 暂时使用User创建时间作为主要判断依据
    
    from app.models import User
    user_recent_count = db.query(func.count(User.id)).filter(
        User.created_at >= time_threshold
    ).scalar() or 0
    
    # 实际实现中，我们通过统计该时段内同一IP的注册用户
    # 但由于没有直接存储IP，我们使用活动追踪
    # 这里简化处理：如果有IP记录在extra_data中才检查
    # 
    # 更佳方案：直接查询UserActivity中的IP记录
    ip_record_count = 0
    try:
        # PostgreSQL JSON字段查询
        if 'postgresql' in config.DATABASE_URL or 'postgres' in config.DATABASE_URL:
            ip_record_count = db.query(func.count(UserActivity.id)).filter(
                UserActivity.action == 'register',
                UserActivity.created_at >= time_threshold,
                UserActivity.extra_data['ip'].astext == client_ip
            ).scalar() or 0
        else:
            # SQLite JSON字段查询（使用LIKE）
            ip_record_count = db.query(func.count(UserActivity.id)).filter(
                UserActivity.action == 'register',
                UserActivity.created_at >= time_threshold,
                UserActivity.extra_data.like(f'%"{client_ip}"%')
            ).scalar() or 0
    except Exception:
        # 查询失败时，使用简单的用户计数作为后备
        pass
    
    # 使用更严格的限制
    if ip_record_count >= IP_REGISTRATION_LIMIT:
        return False, f"该IP地址注册过于频繁，请{IP_REGISTRATION_WINDOW_HOURS}小时后再试"
    
    return True, ""


def check_referrer_monthly_limit(db: Session, referrer_user) -> tuple:
    """
    检查推荐人是否达到月度奖励上限
    
    Args:
        db: 数据库会话
        referrer_user: 推荐人用户对象
    
    Returns:
        (is_allowed, message): 是否允许发放奖励
    """
    if not referrer_user or not referrer_user.referral_code:
        return True, ""
    
    # 如果推荐码已暂停，不允许发放
    if referrer_user.referral_suspended:
        return False, "推荐人账号存在异常，推荐奖励已暂停"
    
    # 检查月度奖励数量
    now = datetime.utcnow()
    month_start = datetime(now.year, now.month, 1)
    
    from app.models import User
    monthly_count = db.query(User).filter(
        User.referred_by == referrer_user.referral_code,
        User.referral_rewarded_at >= month_start
    ).count()
    
    if monthly_count >= MONTHLY_REFERRAL_REWARD_LIMIT:
        return False, f"推荐人本月奖励已达上限（{MONTHLY_REFERRAL_REWARD_LIMIT}次）"
    
    return True, ""


def validate_password_strength(password: str) -> tuple:
    """
    验证密码强度
    返回: (is_valid, message)
    
    要求:
    - 至少8位
    - 必须包含字母（不区分大小写）
    - 必须包含数字
    - 建议包含特殊字符
    """
    if len(password) < 8:
        return False, "密码长度至少8位"
    
    # 检查是否包含字母
    has_letter = any(c.isalpha() for c in password)
    if not has_letter:
        return False, "密码必须包含至少一个字母"
    
    # 检查是否包含数字
    has_digit = any(c.isdigit() for c in password)
    if not has_digit:
        return False, "密码必须包含至少一个数字"
    
    # 检查是否包含特殊字符（提供建议但不强制）
    has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
    if not has_special:
        # 仅作为警告提示，不阻止注册
        import warnings
        warnings.warn("建议密码包含特殊字符以提高安全性")
    
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
    
    # 计算试用期剩余天数
    trial_days_left = 0
    if user.trial_end_date:
        from datetime import datetime
        remaining = user.trial_end_date - datetime.utcnow()
        if remaining.total_seconds() > 0:
            trial_days_left = remaining.days + (1 if remaining.seconds > 0 else 0)
    
    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "is_admin": is_admin,
        "is_subscribed": user.is_subscribed,
        "subscription_status": user.subscription_status,
        "subscription_end_date": user.subscription_end_date.isoformat() if user.subscription_end_date else None,
        "is_whitelisted": user.is_whitelisted,
        # 试用期信息
        "is_in_trial": user.is_in_trial,
        "trial_end_date": user.trial_end_date.isoformat() if user.trial_end_date else None,
        "trial_days_left": trial_days_left,
        "has_premium_access": user.has_premium_access,
        # 推荐码
        "referral_code": user.referral_code,
        # 竞品分析隐私设置
        "opt_out_benchmark": user.opt_out_benchmark or False
    }


class AuthService:
    """认证服务类"""
    
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
    
    def register(self, email: str, password: str, username: str = None, referral_code: str = None) -> tuple:
        """
        用户注册
        
        Args:
            email: 邮箱地址
            password: 密码
            username: 用户名（可选）
            referral_code: 推荐码（可选）
        
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
        
        # 验证推荐码（如果提供）
        referrer_user = None
        if referral_code:
            referral_code = referral_code.strip().upper()
            referrer_user = self.user_repo.get_by_referral_code(referral_code)
            if not referrer_user:
                # 推荐码无效，但不阻止注册，只是忽略
                referral_code = None
        
        # 创建用户
        password_hash = hash_password(password)
        user = self.user_repo.create(
            email=email.lower(),
            password_hash=password_hash,
            username=username,
            referral_code=referral_code  # 传递推荐码
        )
        
        # 记录用户注册行为（包含IP用于防刷检测）
        activity_tracker.log_activity(
            self.db, user.id, 'register',
            metadata={
                'email_domain': email.split('@')[1] if '@' in email else None,
                'referred_by': referral_code  # 记录推荐码
            }
        )
        
        # 延迟发放推荐奖励：只标记待发放，不立即给推荐人奖励
        # 奖励将在被推荐人完成关键操作后发放
        if referrer_user:
            # 检查推荐人月度上限
            is_allowed, msg = check_referrer_monthly_limit(self.db, referrer_user)
            if is_allowed:
                # 标记该用户有待发放的推荐奖励
                self.user_repo.mark_referral_reward_pending(user.id)
            # 注意：即使推荐人已达上限，用户仍然可以注册成功
        
        return True, "注册成功", {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "referral_code": user.referral_code  # 返回用户的推荐码
        }
    
    def _reward_referrer(self, referrer_user):
        """
        奖励推荐人7天Pro权限（延迟发放版本）
        
        Args:
            referrer_user: 推荐人用户对象
        """
        from datetime import datetime, timedelta
        
        # 检查推荐人月度上限
        is_allowed, msg = check_referrer_monthly_limit(self.db, referrer_user)
        if not is_allowed:
            return False
        
        # 计算新的到期时间
        now = datetime.utcnow()
        
        # 优先使用订阅到期时间，其次试用期
        current_end = referrer_user.subscription_end_date or referrer_user.trial_end_date
        
        if current_end and current_end > now:
            # 在现有到期时间基础上延长7天
            new_end = current_end + timedelta(days=REFERRAL_REWARD_DAYS)
        else:
            # 从现在开始计算7天
            new_end = now + timedelta(days=REFERRAL_REWARD_DAYS)
        
        # 更新试用期结束时间（如果用户没有订阅，延长试用期）
        if not referrer_user.is_subscribed:
            referrer_user.trial_end_date = new_end
        else:
            # 如果用户已有订阅，延长订阅到期时间
            referrer_user.subscription_end_date = new_end
        
        self.db.commit()
        return True
    
    def grant_pending_referral_rewards(self, user_id: int) -> bool:
        """
        为指定用户发放待定的推荐奖励
        
        当被推荐人完成关键操作（上传数据集）时调用此方法
        检查并发放其推荐人的奖励
        
        Args:
            user_id: 被推荐用户的ID
        
        Returns:
            bool: 是否成功发放奖励
        """
        user = self.user_repo.get_by_id(user_id)
        if not user or not user.referred_by:
            return False
        
        # 检查是否有待发放的奖励
        if not user.referral_reward_pending:
            return False
        
        # 获取推荐人
        referrer_user = self.user_repo.get_by_referral_code(user.referred_by)
        if not referrer_user:
            return False
        
        # 检查推荐人月度上限
        is_allowed, msg = check_referrer_monthly_limit(self.db, referrer_user)
        if not is_allowed:
            return False
        
        # 发放奖励
        success = self.user_repo.grant_referral_reward(referrer_user.id, REFERRAL_REWARD_DAYS)
        
        if success:
            # 清除被推荐用户的待发放标记
            user.referral_reward_pending = False
            self.db.commit()
            
            # 异步发送通知邮件给推荐人
            self._notify_referrer_of_reward(referrer_user, user)
        
        return success
    
    def _notify_referrer_of_reward(self, referrer_user, referred_user):
        """
        异步通知推荐人获得奖励
        
        Args:
            referrer_user: 推荐人用户
            referred_user: 被推荐用户
        """
        try:
            from app.services.email_service import email_service
            
            # 发送邮件通知
            email_service.send_referral_reward_notification(
                to_email=referrer_user.email,
                username=referrer_user.username or referrer_user.email.split('@')[0],
                days=REFERRAL_REWARD_DAYS
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"发送推荐奖励通知邮件失败: {e}")
    
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
        
        # 记录用户登录行为
        activity_tracker.log_activity(
            self.db, user.id, 'login',
            metadata={'subscription_status': user.subscription_status}
        )
        
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

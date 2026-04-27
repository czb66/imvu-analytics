"""
推荐系统增强服务 - 里程碑奖励和排行榜功能
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from app.models import User, UserFeedback

# 配置日志
logger = logging.getLogger(__name__)

# 里程碑定义
MILESTONES = [
    {
        "level": 3,
        "name": {"en": "Promoter Pro", "zh": "推广达人"},
        "days": 14,
        "badge": "🌟",
        "description": {
            "en": "Get 3 successful referrals! +14 days Pro + 'Promoter Pro' badge",
            "zh": "成功推荐3人！+14天Pro会员 + '推广达人'徽章"
        }
    },
    {
        "level": 5,
        "name": {"en": "Elite Promoter", "zh": "精英推广"},
        "days": 30,
        "badge": "💎",
        "description": {
            "en": "Get 5 successful referrals! +30 days Pro + Custom referral code suffix",
            "zh": "成功推荐5人！+30天Pro会员 + 自定义推荐码后缀"
        }
    },
    {
        "level": 10,
        "name": {"en": "Star Promoter", "zh": "明星推广"},
        "days": 90,
        "badge": "👑",
        "description": {
            "en": "Get 10 successful referrals! +90 days Pro + 'Star Promoter' badge",
            "zh": "成功推荐10人！+90天Pro会员 + '明星推广'徽章"
        }
    },
    {
        "level": 20,
        "name": {"en": "Legendary Promoter", "zh": "传奇推广"},
        "days": 365,
        "badge": "🏆",
        "description": {
            "en": "Get 20 successful referrals! +365 days Pro (1 year FREE!)",
            "zh": "成功推荐20人！+365天Pro会员（整整一年免费！）"
        }
    }
]


def get_milestone_by_level(level: int) -> Optional[dict]:
    """根据等级获取里程碑定义"""
    for m in MILESTONES:
        if m["level"] == level:
            return m
    return None


def get_user_milestone_level(user: User) -> int:
    """
    计算用户的当前里程碑等级
    根据成功推荐人数（referral_rewarded_at不为空的用户）
    """
    if not user.referral_code:
        return 0
    
    # 统计已获得奖励的推荐用户数量
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        count = db.query(User).filter(
            User.referred_by == user.referral_code,
            User.referral_rewarded_at.isnot(None)
        ).count()
    finally:
        db.close()
    
    # 找出最高等级的里程碑
    current_level = 0
    for m in MILESTONES:
        if count >= m["level"]:
            current_level = m["level"]
    
    return current_level


def get_milestone_progress(user: User) -> dict:
    """
    获取用户的里程碑进度
    """
    if not user.referral_code:
        return {
            "current_level": 0,
            "next_level": MILESTONES[0]["level"] if MILESTONES else None,
            "referral_count": 0,
            "required_for_next": MILESTONES[0]["level"] if MILESTONES else None,
            "progress_percent": 0,
            "milestones": [],
            "has_unclaimed": False
        }
    
    # 获取成功推荐数量
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        referral_count = db.query(User).filter(
            User.referred_by == user.referral_code,
            User.referral_rewarded_at.isnot(None)
        ).count()
    finally:
        db.close()
    
    # 构建里程碑状态
    milestones_status = []
    for m in MILESTONES:
        is_unlocked = referral_count >= m["level"]
        is_claimed = is_unlocked and (user.referral_milestone_claimed and user.referral_milestone >= m["level"])
        
        milestones_status.append({
            "level": m["level"],
            "name": m["name"],
            "days": m["days"],
            "badge": m["badge"],
            "description": m["description"],
            "is_unlocked": is_unlocked,
            "is_claimed": is_claimed,
            "is_current": user.referral_milestone == m["level"]
        })
    
    # 计算下一个里程碑
    next_milestone = None
    for m in MILESTONES:
        if m["level"] > referral_count:
            next_milestone = m
            break
    
    # 计算进度百分比
    if next_milestone:
        prev_requirement = 0
        for m in MILESTONES:
            if m["level"] > referral_count:
                break
            prev_requirement = m["level"]
        progress_percent = min(100, round((referral_count - prev_requirement) / (next_milestone["level"] - prev_requirement) * 100))
        required_for_next = next_milestone["level"]
    else:
        progress_percent = 100
        required_for_next = None
    
    # 是否有未领取的奖励
    has_unclaimed = any(
        m["is_unlocked"] and not m["is_claimed"]
        for m in milestones_status
    )
    
    return {
        "current_level": user.referral_milestone,
        "next_level": next_milestone["level"] if next_milestone else None,
        "referral_count": referral_count,
        "required_for_next": required_for_next,
        "progress_percent": progress_percent,
        "milestones": milestones_status,
        "has_unclaimed": has_unclaimed
    }


def claim_milestone_reward(db: Session, user: User) -> dict:
    """
    领取里程碑奖励
    
    返回: {success: bool, message: str, reward: dict}
    """
    if not user.referral_code:
        return {
            "success": False,
            "message": "您还没有推荐码，无法领取奖励",
            "reward": None
        }
    
    # 检查是否有未领取的里程碑
    current_level = get_user_milestone_level(user)
    
    if current_level == 0:
        return {
            "success": False,
            "message": "您还没有达到任何里程碑",
            "reward": None
        }
    
    # 找到最新的可领取里程碑
    milestone_to_claim = None
    for m in reversed(MILESTONES):
        if current_level >= m["level"]:
            if not (user.referral_milestone_claimed and user.referral_milestone >= m["level"]):
                milestone_to_claim = m
                break
    
    if not milestone_to_claim:
        return {
            "success": False,
            "message": "所有里程碑奖励已领取",
            "reward": None
        }
    
    try:
        # 计算新的到期时间
        now = datetime.utcnow()
        current_end = user.subscription_end_date or user.trial_end_date
        
        if current_end and current_end > now:
            new_end = current_end + timedelta(days=milestone_to_claim["days"])
        else:
            new_end = now + timedelta(days=milestone_to_claim["days"])
        
        # 更新用户
        user.subscription_end_date = new_end
        user.referral_milestone = milestone_to_claim["level"]
        user.referral_milestone_claimed = True
        db.commit()
        
        logger.info(f"用户 {user.id} 领取了里程碑 {milestone_to_claim['level']} 奖励: +{milestone_to_claim['days']}天")
        
        return {
            "success": True,
            "message": f"恭喜获得 {milestone_to_claim['days']} 天 Pro 会员！",
            "reward": {
                "level": milestone_to_claim["level"],
                "name": milestone_to_claim["name"],
                "days": milestone_to_claim["days"],
                "badge": milestone_to_claim["badge"],
                "new_end_date": new_end.isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"领取里程碑奖励失败: {e}")
        db.rollback()
        return {
            "success": False,
            "message": "领取失败，请稍后重试",
            "reward": None
        }


def get_referral_leaderboard(db: Session, limit: int = 20) -> List[dict]:
    """
    获取推荐排行榜（Top N）
    只显示用户名+推荐数，不显示具体收益
    """
    # 统计每个用户的成功推荐数量
    successful_referrals = db.query(
        User.referred_by,
        func.count(User.id).label("count")
    ).filter(
        User.referred_by.isnot(None),
        User.referral_rewarded_at.isnot(None)
    ).group_by(User.referred_by).subquery()
    
    # 获取前N名
    leaderboard = db.query(
        User.username,
        User.email,
        User.referral_code,
        User.referral_anonymous,
        successful_referrals.c.count.label("referral_count")
    ).join(
        successful_referrals,
        User.referral_code == successful_referrals.c.referred_by
    ).order_by(
        desc(successful_referrals.c.count)
    ).limit(limit).all()
    
    result = []
    for rank, entry in enumerate(leaderboard, 1):
        # 处理匿名用户
        display_name = "匿名用户" if entry.referral_anonymous else (entry.username or entry.email.split("@")[0])
        
        result.append({
            "rank": rank,
            "display_name": display_name,
            "referral_count": entry.referral_count,
            "is_anonymous": entry.referral_anonymous
        })
    
    return result


def get_user_leaderboard_rank(db: Session, user_id: int) -> Optional[dict]:
    """
    获取用户当前的排行榜排名
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.referral_code:
        return None
    
    # 统计成功推荐数
    referral_count = db.query(User).filter(
        User.referred_by == user.referral_code,
        User.referral_rewarded_at.isnot(None)
    ).count()
    
    if referral_count == 0:
        return {"rank": None, "referral_count": 0}
    
    # 计算排名
    rank = db.query(func.count()).filter(
        User.referred_by.isnot(None),
        User.referral_rewarded_at.isnot(None)
    ).group_by(User.referred_by).having(
        func.count(User.id) > referral_count
    ).count() + 1
    
    return {
        "rank": rank,
        "referral_count": referral_count
    }


def get_enhanced_referral_stats(db: Session, user_id: int) -> dict:
    """
    获取增强的推荐统计
    """
    from app.database import UserRepository
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_id)
    
    if not user:
        return {"error": "用户不存在"}
    
    # 基础统计
    base_stats = user_repo.get_referral_stats(user_id)
    
    # 里程碑进度
    milestone_progress = get_milestone_progress(user)
    
    # 排行榜信息
    leaderboard_info = get_user_leaderboard_rank(db, user_id)
    
    # 待发放奖励
    pending_count = db.query(User).filter(
        User.referred_by == user.referral_code,
        User.referral_reward_pending == True
    ).count() if user.referral_code else 0
    
    # 成功推荐数
    success_count = base_stats.get("referral_count", 0)
    
    return {
        "referral_code": base_stats.get("referral_code"),
        "referral_suspended": base_stats.get("referral_suspended", False),
        "total_referrals": success_count + pending_count,
        "successful_referrals": success_count,
        "pending_rewards": pending_count,
        "monthly_rewards": base_stats.get("monthly_rewards", 0),
        "monthly_limit": 5,
        "milestone": milestone_progress,
        "leaderboard": leaderboard_info
    }

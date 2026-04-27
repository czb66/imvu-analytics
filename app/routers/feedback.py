"""
反馈和NPS评分路由 - 收集用户反馈和满意度评分
"""

import logging
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from pydantic import BaseModel, Field

from app.database import get_db, UserRepository
from app.services.auth import get_current_user
from app.models import UserFeedback

# 配置日志
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/feedback", tags=["反馈"])

# ==================== 请求/响应模型 ====================

class SubmitFeedbackRequest(BaseModel):
    """提交反馈请求"""
    nps_score: Optional[int] = Field(None, ge=0, le=10, description="NPS评分 0-10")
    feedback_type: Optional[str] = Field(None, description="反馈类型: bug/feature/general")
    content: Optional[str] = Field(None, min_length=10, description="反馈内容（至少10字）")
    page_url: Optional[str] = Field(None, max_length=500, description="反馈来源页面")


class FeedbackListResponse(BaseModel):
    """反馈列表响应"""
    id: int
    user_id: int
    username: Optional[str]
    email: Optional[str]
    nps_score: Optional[int]
    feedback_type: Optional[str]
    content: Optional[str]
    page_url: Optional[str]
    created_at: datetime


# ==================== 辅助函数 ====================

def check_daily_feedback_limit(db: Session, user_id: int) -> bool:
    """
    检查用户今天的反馈提交次数
    返回: 是否超过限制（每天最多3条）
    """
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    count = db.query(UserFeedback).filter(
        UserFeedback.user_id == user_id,
        UserFeedback.created_at >= today_start
    ).count()
    
    return count >= 3


def should_show_nps_widget(db: Session, user_id: int) -> dict:
    """
    检查用户是否应该显示NPS弹窗
    规则：注册7天后且未提交过NPS的用户才显示
    返回: {show: bool, reason: str}
    """
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_id)
    
    if not user:
        return {"show": False, "reason": "user_not_found"}
    
    # 检查注册时间是否满7天
    if user.created_at:
        days_since_register = (datetime.utcnow() - user.created_at).days
        if days_since_register < 7:
            return {"show": False, "reason": "not_qualified", "days_remaining": 7 - days_since_register}
    
    # 检查是否已提交过NPS
    has_nps = db.query(UserFeedback).filter(
        UserFeedback.user_id == user_id,
        UserFeedback.nps_score.isnot(None)
    ).first()
    
    if has_nps:
        return {"show": False, "reason": "already_submitted"}
    
    return {"show": True, "reason": "qualified"}


# ==================== 路由 ====================

@router.post("/submit")
async def submit_feedback(
    request: SubmitFeedbackRequest,
    http_request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    提交用户反馈/NPS评分
    
    - nps_score: NPS评分 0-10（可选）
    - feedback_type: 反馈类型 bug/feature/general（可选）
    - content: 反馈内容（可选，但NPS提交时建议填写）
    - page_url: 反馈来源页面（可选）
    
    限流：每个用户每天最多3条反馈
    """
    user_id = current_user["id"]
    
    # 验证：至少有一个有效字段
    if not any([request.nps_score is not None, request.feedback_type, request.content]):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"success": False, "message": "请提供反馈内容或NPS评分"}
        )
    
    # 限流检查
    if check_daily_feedback_limit(db, user_id):
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"success": False, "message": "今天反馈次数已达上限（3条/天），请明天再试"}
        )
    
    # 验证 NPS 评分
    if request.nps_score is not None:
        if request.nps_score < 0 or request.nps_score > 10:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"success": False, "message": "NPS评分必须在0-10之间"}
            )
    
    # 验证反馈内容长度
    if request.content and len(request.content) < 10:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"success": False, "message": "反馈内容至少需要10个字符"}
        )
    
    # 获取页面URL
    page_url = request.page_url
    if not page_url:
        page_url = http_request.headers.get("referer", "")[:500]
    
    try:
        # 创建反馈记录
        feedback = UserFeedback(
            user_id=user_id,
            nps_score=request.nps_score,
            feedback_type=request.feedback_type,
            content=request.content,
            page_url=page_url
        )
        db.add(feedback)
        db.commit()
        db.refresh(feedback)
        
        logger.info(f"用户 {user_id} 提交了反馈: NPS={request.nps_score}, type={request.feedback_type}")
        
        return {
            "success": True,
            "message": "反馈提交成功，感谢您的反馈！",
            "data": {
                "id": feedback.id,
                "created_at": feedback.created_at.isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"提交反馈失败: {e}")
        db.rollback()
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "message": "提交失败，请稍后重试"}
        )


@router.get("/nps-widget")
async def get_nps_widget_config(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取NPS弹窗配置（是否应该显示）
    
    规则：注册7天后且未提交过NPS的用户才显示
    """
    user_id = current_user["id"]
    config = should_show_nps_widget(db, user_id)
    
    # 检查 localStorage 缓存
    return {
        "success": True,
        "data": {
            "should_show": config["show"],
            "reason": config.get("reason"),
            "days_remaining": config.get("days_remaining"),
            "dismissed_until": None  # 前端可自行处理 localStorage 缓存
        }
    }


# ==================== 管理员路由 ====================

admin_router = APIRouter(prefix="/api/admin", tags=["管理"])


@admin_router.get("/feedbacks")
async def get_feedbacks(
    page: int = 1,
    page_size: int = 20,
    feedback_type: Optional[str] = None,
    has_nps: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    管理员获取所有反馈（分页）
    """
    # 权限检查
    if not current_user.get("is_admin"):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"success": False, "message": "需要管理员权限"}
        )
    
    query = db.query(UserFeedback).order_by(desc(UserFeedback.created_at))
    
    # 筛选
    if feedback_type:
        query = query.filter(UserFeedback.feedback_type == feedback_type)
    
    if has_nps is not None:
        if has_nps:
            query = query.filter(UserFeedback.nps_score.isnot(None))
        else:
            query = query.filter(UserFeedback.nps_score.is_(None))
    
    # 总数
    total = query.count()
    
    # 分页
    offset = (page - 1) * page_size
    feedbacks = query.offset(offset).limit(page_size).all()
    
    # 获取用户信息
    user_repo = UserRepository(db)
    result = []
    for fb in feedbacks:
        user = user_repo.get_by_id(fb.user_id)
        result.append({
            "id": fb.id,
            "user_id": fb.user_id,
            "username": user.username if user else None,
            "email": user.email if user else None,
            "nps_score": fb.nps_score,
            "feedback_type": fb.feedback_type,
            "content": fb.content,
            "page_url": fb.page_url,
            "created_at": fb.created_at.isoformat() if fb.created_at else None
        })
    
    return {
        "success": True,
        "data": {
            "items": result,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    }


@admin_router.get("/nps-summary")
async def get_nps_summary(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    管理员获取NPS汇总统计
    """
    if not current_user.get("is_admin"):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"success": False, "message": "需要管理员权限"}
        )
    
    # 计算日期范围
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # 获取所有有NPS评分的反馈
    nps_query = db.query(UserFeedback).filter(
        UserFeedback.nps_score.isnot(None),
        UserFeedback.created_at >= start_date
    )
    
    nps_records = nps_query.all()
    total_nps = len(nps_records)
    
    if total_nps == 0:
        return {
            "success": True,
            "data": {
                "period_days": days,
                "total_responses": 0,
                "average_score": 0,
                "promoter_percent": 0,
                "passive_percent": 0,
                "detractor_percent": 0,
                "trend": [],
                "by_type": {},
                "by_page": {}
            }
        }
    
    # 计算平均分
    total_score = sum(r.nps_score for r in nps_records)
    avg_score = total_score / total_nps
    
    # 计算 Promoter (9-10) / Passive (7-8) / Detractor (0-6)
    promoters = len([r for r in nps_records if r.nps_score >= 9])
    passives = len([r for r in nps_records if 7 <= r.nps_score <= 8])
    detractors = len([r for r in nps_records if r.nps_score <= 6])
    
    promoter_pct = round(promoters / total_nps * 100, 1)
    passive_pct = round(passives / total_nps * 100, 1)
    detractor_pct = round(detractors / total_nps * 100, 1)
    
    # 按类型统计
    by_type = {}
    for fb in nps_records:
        fb_type = fb.feedback_type or "general"
        if fb_type not in by_type:
            by_type[fb_type] = {"count": 0, "total_score": 0}
        by_type[fb_type]["count"] += 1
        by_type[fb_type]["total_score"] += fb.nps_score
    
    for fb_type in by_type:
        count = by_type[fb_type]["count"]
        by_type[fb_type]["avg_score"] = round(by_type[fb_type]["total_score"] / count, 1)
        by_type[fb_type]["percent"] = round(count / total_nps * 100, 1)
    
    # 按页面统计
    by_page = {}
    for fb in nps_records:
        if fb.page_url:
            # 简化URL路径
            path = fb.page_url.split("?")[0].split("/")[-1] or "home"
            if path not in by_page:
                by_page[path] = {"count": 0, "total_score": 0}
            by_page[path]["count"] += 1
            by_page[path]["total_score"] += fb.nps_score
    
    for path in by_page:
        count = by_page[path]["count"]
        by_page[path]["avg_score"] = round(by_page[path]["total_score"] / count, 1)
    
    # 按月/周趋势
    trend = []
    if total_nps >= 5:
        # 按周分组
        weeks = {}
        for fb in nps_records:
            week_start = fb.created_at - timedelta(days=fb.created_at.weekday())
            week_key = week_start.strftime("%Y-W%W")
            if week_key not in weeks:
                weeks[week_key] = []
            weeks[week_key].append(fb.nps_score)
        
        for week_key in sorted(weeks.keys()):
            scores = weeks[week_key]
            trend.append({
                "period": week_key,
                "count": len(scores),
                "avg_score": round(sum(scores) / len(scores), 1)
            })
    
    return {
        "success": True,
        "data": {
            "period_days": days,
            "total_responses": total_nps,
            "average_score": round(avg_score, 1),
            "promoter_percent": promoter_pct,
            "passive_percent": passive_pct,
            "detractor_percent": detractor_pct,
            "nps_score": promoter_pct - detractor_pct,  # NPS = %Promoters - %Detractors
            "trend": trend,
            "by_type": by_type,
            "by_page": by_page
        }
    }

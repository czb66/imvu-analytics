"""
后台管理路由 - 提供管理员功能
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import HTMLResponse
from fastapi import Request
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
from datetime import datetime, timedelta
from typing import Optional
import logging

from app.database import get_db, UserRepository
from app.services.admin import require_admin
from app.services.auth import get_current_user
import config

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/admin", tags=["后台管理"])


@router.get("/stats")
async def get_admin_stats(
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    获取管理后台统计数据
    - 总用户数
    - 已订阅用户数
    - 本周新增用户数
    """
    try:
        from app.models import User
        
        # 总用户数
        total_users = db.query(User).count()
        
        # 已订阅用户数 (active subscription)
        subscribed_users = db.query(User).filter(
            User.subscription_status == 'active'
        ).count()
        
        # 本周新增用户数
        week_ago = datetime.utcnow() - timedelta(days=7)
        weekly_new_users = db.query(User).filter(
            User.created_at >= week_ago
        ).count()
        
        return {
            "success": True,
            "data": {
                "total_users": total_users,
                "subscribed_users": subscribed_users,
                "weekly_new_users": weekly_new_users
            }
        }
    except Exception as e:
        logger.error(f"获取统计数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取统计数据失败: {str(e)}")


@router.get("/users")
async def get_admin_users(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    search: Optional[str] = Query(None, description="搜索关键词（邮箱或用户名）"),
    subscription_status: Optional[str] = Query(None, description="订阅状态过滤"),
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    获取用户列表（分页）
    """
    try:
        from app.models import User
        
        query = db.query(User)
        
        # 搜索过滤
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    User.email.ilike(search_pattern),
                    User.username.ilike(search_pattern)
                )
            )
        
        # 订阅状态过滤
        if subscription_status:
            if subscription_status == 'subscribed':
                query = query.filter(User.subscription_status == 'active')
            elif subscription_status == 'not_subscribed':
                query = query.filter(User.subscription_status != 'active')
        
        # 获取总数
        total = query.count()
        
        # 分页
        offset = (page - 1) * page_size
        users = query.order_by(desc(User.created_at)).offset(offset).limit(page_size).all()
        
        # 转换数据
        user_list = []
        for user in users:
            user_list.append({
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "is_active": user.is_active,
                "is_admin": user.is_admin,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "last_login": user.last_login.isoformat() if user.last_login else None,
                "subscription_status": user.subscription_status,
                "subscription_end_date": user.subscription_end_date.isoformat() if user.subscription_end_date else None,
                "is_subscribed": user.is_subscribed
            })
        
        return {
            "success": True,
            "data": {
                "users": user_list,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size
            }
        }
    except Exception as e:
        logger.error(f"获取用户列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取用户列表失败: {str(e)}")


@router.post("/users/{user_id}/toggle-subscription")
async def toggle_user_subscription(
    user_id: int,
    action: str = Query(..., description="操作：activate 或 deactivate"),
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    手动开启/关闭用户订阅
    """
    try:
        from app.models import User
        
        user_repo = UserRepository(db)
        user = user_repo.get_by_id(user_id)
        
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        if action == "activate":
            user.subscription_status = 'active'
            user.subscription_end_date = datetime.utcnow() + timedelta(days=30)  # 默认30天
            message = "订阅已激活"
        elif action == "deactivate":
            user.subscription_status = 'canceled'
            user.subscription_end_date = datetime.utcnow()
            message = "订阅已取消"
        else:
            raise HTTPException(status_code=400, detail="无效的操作")
        
        db.commit()
        
        return {
            "success": True,
            "message": message,
            "data": {
                "user_id": user.id,
                "subscription_status": user.subscription_status,
                "subscription_end_date": user.subscription_end_date.isoformat() if user.subscription_end_date else None
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"切换订阅状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"操作失败: {str(e)}")


@router.post("/users/{user_id}/toggle-admin")
async def toggle_user_admin(
    user_id: int,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    切换用户管理员权限
    """
    try:
        user_repo = UserRepository(db)
        user = user_repo.get_by_id(user_id)
        
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 防止取消自己的管理员权限
        if user.id == current_user["id"]:
            raise HTTPException(status_code=400, detail="不能修改自己的管理员权限")
        
        user.is_admin = not user.is_admin
        db.commit()
        
        return {
            "success": True,
            "message": f"管理员权限已{'授予' if user.is_admin else '撤销'}",
            "data": {
                "user_id": user.id,
                "is_admin": user.is_admin
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"切换管理员权限失败: {e}")
        raise HTTPException(status_code=500, detail=f"操作失败: {str(e)}")


@router.post("/users/{user_id}/toggle-whitelist")
async def toggle_user_whitelist(
    user_id: int,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    切换用户白名单状态
    
    白名单用户可以跳过订阅检查，免费使用所有功能
    """
    try:
        user_repo = UserRepository(db)
        user = user_repo.get_by_id(user_id)
        
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        user.is_whitelisted = not user.is_whitelisted
        db.commit()
        
        logger.info(f"管理员 {current_user.get('email')} {'添加' if user.is_whitelisted else '移除'}用户 {user.email} 的白名单权限")
        
        return {
            "success": True,
            "message": f"白名单权限已{'授予' if user.is_whitelisted else '撤销'}",
            "data": {
                "user_id": user.id,
                "email": user.email,
                "is_whitelisted": user.is_whitelisted
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"切换白名单权限失败: {e}")
        raise HTTPException(status_code=500, detail=f"操作失败: {str(e)}")
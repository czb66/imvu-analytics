"""
认证路由 - 处理用户注册、登录、登出
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session
import logging

from app.database import get_db
from app.services.auth import AuthService, get_current_user
from app.services.activity_tracker import activity_tracker
from app.core.limiter import limiter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["认证"])


# ==================== 请求/响应模型 ====================

class RegisterRequest(BaseModel):
    """注册请求"""
    email: EmailStr = Field(..., description="邮箱地址")
    password: str = Field(..., min_length=8, description="密码（至少8位）")
    username: str = Field(None, max_length=100, description="用户名（可选）")
    referral_code: str = Field(None, max_length=20, description="推荐码（可选）")


class LoginRequest(BaseModel):
    """登录请求"""
    email: EmailStr = Field(..., description="邮箱地址")
    password: str = Field(..., description="密码")
    remember_me: bool = Field(False, description="记住我")


class UserResponse(BaseModel):
    """用户响应"""
    id: int
    email: str
    username: str = None


class AuthResponse(BaseModel):
    """认证响应"""
    success: bool
    message: str
    data: dict = None


# ==================== API路由 ====================

def get_client_ip(request: Request) -> str:
    """
    获取客户端真实IP地址
    
    优先从 X-Forwarded-For 头获取（反向代理场景），
    否则使用 request.client.host
    """
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # X-Forwarded-For 可能包含多个IP，取第一个（最原始的）
        return forwarded_for.split(",")[0].strip()
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()
    return request.client.host if request.client else "unknown"


@router.post("/register", response_model=AuthResponse)
@limiter.limit("3/minute")  # 注册限制：3次/分钟
async def register(request: Request, register_request: RegisterRequest, db: Session = Depends(get_db)):
    """
    用户注册（速率限制：3次/分钟）
    
    - **email**: 邮箱地址（唯一）
    - **password**: 密码（至少8位，包含字母和数字）
    - **username**: 用户名（可选）
    - **referral_code**: 推荐码（可选）
    """
    try:
        # 获取客户端IP
        client_ip = get_client_ip(request)
        
        # 检查IP注册限制
        from app.services.auth import check_ip_registration_limit
        is_allowed, limit_msg = check_ip_registration_limit(db, client_ip)
        if not is_allowed:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"success": False, "message": limit_msg}
            )
        
        auth_service = AuthService(db)
        success, message, data = auth_service.register(
            email=register_request.email,
            password=register_request.password,
            username=register_request.username,
            referral_code=register_request.referral_code
        )
        
        if not success:
            # 检查是否是因为推荐码问题
            if "推荐码" in message and "暂停" in message:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={"success": False, "message": message}
                )
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"success": False, "message": message}
            )
        
        return {
            "success": True,
            "message": message,
            "data": data
        }
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"注册失败: {e}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "message": "操作失败，请稍后重试"}
        )


@router.post("/login", response_model=AuthResponse)
@limiter.limit("5/minute")  # 登录限制：5次/分钟（防暴力破解）
async def login(request: Request, login_request: LoginRequest, db: Session = Depends(get_db)):
    """
    用户登录（速率限制：5次/分钟）
    
    - **email**: 邮箱地址
    - **password**: 密码
    - **remember_me**: 记住我（延长Token有效期）
    """
    try:
        auth_service = AuthService(db)
        success, message, data = auth_service.login(
            email=login_request.email,
            password=login_request.password,
            remember_me=login_request.remember_me
        )
        
        if not success:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"success": False, "message": message}
            )
        
        return {
            "success": True,
            "message": message,
            "data": data
        }
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        logger.error(f"登录异常: {e}\n{error_detail}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "message": "登录失败，请稍后重试"}
        )


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    用户登出
    
    注意：由于使用JWT无状态认证，后端不需要做任何处理
    客户端只需要删除本地存储的Token即可
    """
    # 记录用户登出行为
    activity_tracker.log_activity(db, current_user.get('id'), 'logout')
    
    return {
        "success": True,
        "message": "已安全退出"
    }


@router.get("/me", response_model=AuthResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    """
    获取当前登录用户信息
    """
    # 添加试用期相关信息
    from datetime import datetime
    if "trial_end_date" in current_user and current_user["trial_end_date"]:
        trial_end = current_user["trial_end_date"]
        if isinstance(trial_end, str):
            trial_end = datetime.fromisoformat(trial_end.replace("Z", "+00:00"))
        if trial_end:
            now = datetime.utcnow()
            current_user["is_in_trial"] = trial_end > now
            if trial_end > now:
                delta = trial_end - now
                current_user["trial_days_left"] = delta.days + 1
            else:
                current_user["trial_days_left"] = 0
    else:
        current_user["is_in_trial"] = False
        current_user["trial_days_left"] = 0
    
    return {
        "success": True,
        "message": "获取成功",
        "data": current_user
    }


@router.post("/check-email")
async def check_email(request: dict, db: Session = Depends(get_db)):
    """
    检查邮箱是否已被注册
    
    - **email**: 邮箱地址
    """
    from app.services.auth import validate_email
    from app.database import UserRepository
    
    email = request.get('email', '')
    
    if not email or not validate_email(email):
        return {"exists": False, "valid": False}
    
    user_repo = UserRepository(db)
    exists = user_repo.email_exists(email)
    
    return {"exists": exists, "valid": True}

# 白名单初始化API已禁用 - 请通过数据库直接管理

@router.get("/referral-stats")
async def get_referral_stats(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户推荐统计
    
    返回用户的推荐码和推荐人数
    """
    from app.database import UserRepository
    user_repo = UserRepository(db)
    
    stats = user_repo.get_referral_stats(current_user["id"])
    
    return {
        "success": True,
        "message": "获取成功",
        "data": stats
    }


@router.get("/profile")
async def get_profile(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户个人中心信息
    """
    from app.database import UserRepository
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(current_user["id"])
    
    if not user:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"success": False, "message": "用户不存在"}
        )
    
    return {
        "success": True,
        "message": "获取成功",
        "data": {
            "id": user.id,
            "email": user.email,
            "username": user.username or "用户",
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "last_login": user.last_login.isoformat() if hasattr(user, 'last_login') and user.last_login else None
        }
    }


class UpdateProfileRequest(BaseModel):
    """更新用户信息请求"""
    username: Optional[str] = Field(None, max_length=50, description="用户名")


@router.put("/profile")
async def update_profile(
    request: UpdateProfileRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新用户信息
    """
    from app.database import UserRepository
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(current_user["id"])
    
    if not user:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"success": False, "message": "用户不存在"}
        )
    
    # 更新用户名
    if request.username is not None:
        user.username = request.username.strip() if request.username.strip() else None
        db.commit()
    
    return {
        "success": True,
        "message": "用户名更新成功",
        "data": {
            "username": user.username
        }
    }


class OnboardingStepRequest(BaseModel):
    """更新引导步骤请求"""
    step: int = Field(..., ge=0, le=3, description="引导步骤 0=未开始, 1-3=各步骤完成, 3=全部完成")


@router.get("/onboarding")
async def get_onboarding_status(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户引导状态
    
    返回用户当前所在的引导步骤
    """
    from app.database import UserRepository
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(current_user["id"])
    
    if not user:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"success": False, "message": "用户不存在"}
        )
    
    return {
        "success": True,
        "message": "获取成功",
        "data": {
            "onboarding_step": user.onboarding_step or 0,
            "onboarding_completed_at": user.onboarding_completed_at.isoformat() if user.onboarding_completed_at else None
        }
    }


@router.post("/onboarding/step")
async def update_onboarding_step(
    request: OnboardingStepRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新用户引导步骤
    
    - **step**: 引导步骤 (0=未开始, 1=步骤1完成, 2=步骤2完成, 3=全部完成)
    """
    from app.database import UserRepository
    from datetime import datetime
    
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(current_user["id"])
    
    if not user:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"success": False, "message": "用户不存在"}
        )
    
    # 更新引导步骤
    user.onboarding_step = request.step
    
    # 如果完成所有步骤，记录完成时间
    if request.step == 3 and not user.onboarding_completed_at:
        user.onboarding_completed_at = datetime.utcnow()
    
    db.commit()
    
    # 记录用户行为
    activity_tracker.log_activity(db, user.id, f'onboarding_step_{request.step}')
    
    return {
        "success": True,
        "message": "引导步骤已更新",
        "data": {
            "onboarding_step": user.onboarding_step,
            "onboarding_completed_at": user.onboarding_completed_at.isoformat() if user.onboarding_completed_at else None
        }
    }


class ChangePasswordRequest(BaseModel):
    """修改密码请求"""
    old_password: str = Field(..., min_length=8, description="当前密码")
    new_password: str = Field(..., min_length=8, description="新密码（至少8位）")


@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    修改密码
    """
    from passlib.context import CryptContext
    from app.database import UserRepository
    
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(current_user["id"])
    
    if not user:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"success": False, "message": "用户不存在"}
        )
    
    # 验证旧密码
    if not pwd_context.verify(request.old_password, user.password_hash):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"success": False, "message": "当前密码不正确"}
        )
    
    # 更新密码
    user.password_hash = pwd_context.hash(request.new_password)
    db.commit()
    
    return {
        "success": True,
        "message": "密码修改成功"
    }


# ==================== 密码重置 ====================

class ForgotPasswordRequest(BaseModel):
    """忘记密码请求"""
    email: EmailStr = Field(..., description="邮箱地址")


class ValidateTokenRequest(BaseModel):
    """验证Token请求"""
    token: str = Field(..., description="重置令牌")


class ResetPasswordRequest(BaseModel):
    """重置密码请求"""
    token: str = Field(..., description="重置令牌")
    new_password: str = Field(..., min_length=8, description="新密码（至少8位）")


@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """
    忘记密码 - 发送重置邮件
    
    - **email**: 邮箱地址
    """
    import logging
    import secrets
    from datetime import datetime, timedelta
    from app.database import UserRepository
    from app.services.email_service import email_service
    
    logger = logging.getLogger(__name__)
    
    try:
        user_repo = UserRepository(db)
        user = user_repo.get_by_email(request.email)
        
        # 即使用户不存在也返回成功，避免泄露用户信息
        if not user:
            logger.info(f"密码重置请求：邮箱 {request.email}")
            return {
                "success": True,
                "message": "如果该邮箱已注册，您将收到密码重置邮件"
            }
        
        # 生成重置令牌
        reset_token = secrets.token_urlsafe(32)
        # 存储哈希值而非明文
        import hashlib
        reset_token_hash = hashlib.sha256(reset_token.encode()).hexdigest()
        reset_token_expires = datetime.utcnow() + timedelta(hours=1)
        
        # 保存到数据库（存储哈希值）
        user.reset_token = reset_token_hash
        user.reset_token_expires = reset_token_expires
        db.commit()
        
        # 构建重置链接
        reset_url = f"https://imvucreators.com/reset-password?token={reset_token}"
        
        # 发送邮件
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; }}
                .content {{ background: #f8f9fa; padding: 20px; border-radius: 10px; margin-top: 20px; }}
                .button {{ display: inline-block; background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; color: #666; margin-top: 20px; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔐 密码重置</h1>
                </div>
                <div class="content">
                    <p>您好，</p>
                    <p>我们收到了您的密码重置请求。请点击下方按钮重置密码：</p>
                    <p style="text-align: center;">
                        <a href="{reset_url}" class="button">重置密码</a>
                    </p>
                    <p>或复制以下链接到浏览器：</p>
                    <p style="word-break: break-all; background: #e9ecef; padding: 10px; border-radius: 5px; font-size: 12px;">
                        {reset_url}
                    </p>
                    <p><strong>注意：</strong>此链接将在 1 小时后失效。</p>
                    <p>如果您没有请求重置密码，请忽略此邮件。</p>
                </div>
                <div class="footer">
                    <p>此邮件由 IMVU Analytics 自动发送，请勿回复。</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        success, message = email_service.send_report(
            to_emails=[user.email],
            subject="🔐 IMVU Analytics - 密码重置",
            html_content=html_content
        )
        
        if success:
            logger.info(f"密码重置邮件已发送至用户ID: {user.id}")
        else:
            logger.error(f"密码重置邮件发送失败: {message}")
        
        return {
            "success": True,
            "message": "如果该邮箱已注册，您将收到密码重置邮件"
        }
        
    except Exception as e:
        logger.error(f"密码重置失败: {e}", exc_info=True)
        return {
            "success": True,
            "message": "如果该邮箱已注册，您将收到密码重置邮件"
        }


@router.post("/validate-reset-token")
async def validate_reset_token(request: ValidateTokenRequest, db: Session = Depends(get_db)):
    """
    验证重置令牌
    
    - **token**: 重置令牌
    """
    import hashlib
    import hmac
    from datetime import datetime
    from app.database import UserRepository
    
    # 计算令牌哈希
    token_hash = hashlib.sha256(request.token.encode()).hexdigest()
    
    user_repo = UserRepository(db)
    user = user_repo.get_by_reset_token_hash(token_hash)
    
    if not user:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"success": False, "message": "无效的重置链接"}
        )
    
    # 检查令牌是否过期
    if user.reset_token_expires and user.reset_token_expires < datetime.utcnow():
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"success": False, "message": "重置链接已过期，请重新申请"}
        )
    
    return {
        "success": True,
        "message": "令牌有效",
        "data": {
            "email": user.email[:3] + "***" + user.email.split("@")[-1]
        }
    }


@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    """
    重置密码
    
    - **token**: 重置令牌
    - **new_password**: 新密码
    """
    import hashlib
    import logging
    from datetime import datetime
    from app.database import UserRepository
    from app.services.auth import hash_password
    
    logger = logging.getLogger(__name__)
    
    # 计算令牌哈希
    token_hash = hashlib.sha256(request.token.encode()).hexdigest()
    
    user_repo = UserRepository(db)
    user = user_repo.get_by_reset_token_hash(token_hash)
    
    if not user:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"success": False, "message": "无效的重置链接"}
        )
    
    # 检查令牌是否过期
    if user.reset_token_expires and user.reset_token_expires < datetime.utcnow():
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"success": False, "message": "重置链接已过期，请重新申请"}
        )
    
    # 更新密码
    user.password_hash = hash_password(request.new_password)
    user.reset_token = None
    user.reset_token_expires = None
    db.commit()
    
    logger.info(f"密码重置成功: 用户ID {user.id}")
    
    return {
        "success": True,
        "message": "密码重置成功，请使用新密码登录"
    }


# ==================== 报告订阅偏好 ====================

class ReportPreferenceRequest(BaseModel):
    """报告订阅偏好设置请求"""
    report_preference: str = Field(
        ...,
        description="报告订阅偏好: daily(每日)/weekly(每周)/none(取消订阅)"
    )


@router.get("/report-preference")
async def get_report_preference(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的报告订阅偏好
    
    返回: daily, weekly, none
    """
    from app.database import UserRepository
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(current_user["id"])
    
    if not user:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"success": False, "message": "用户不存在"}
        )
    
    return {
        "success": True,
        "message": "获取成功",
        "data": {
            "report_preference": user.report_preference or "weekly"
        }
    }


@router.post("/report-preference")
async def set_report_preference(
    request: ReportPreferenceRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    设置报告订阅偏好
    
    - **report_preference**: daily(每日报告) / weekly(每周报告) / none(取消订阅)
    """
    from app.database import UserRepository
    
    # 验证参数
    valid_prefs = ['daily', 'weekly', 'none']
    if request.report_preference not in valid_prefs:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "message": f"无效的订阅选项，仅支持: {', '.join(valid_prefs)}"
            }
        )
    
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(current_user["id"])
    
    if not user:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"success": False, "message": "用户不存在"}
        )
    
    # 更新订阅偏好
    user.report_preference = request.report_preference
    db.commit()
    
    logger.info(f"用户ID {user.id} 更新报告偏好为: {request.report_preference}")
    
    return {
        "success": True,
        "message": "报告订阅偏好已更新",
        "data": {
            "report_preference": user.report_preference
        }
    }


# ==================== 竞品分析隐私设置 ====================

class BenchmarkPreferenceRequest(BaseModel):
    """竞品分析隐私设置请求"""
    opt_out_benchmark: bool = Field(..., description="是否不参与行业基准计算")


@router.post("/benchmark-preference")
async def set_benchmark_preference(
    request: BenchmarkPreferenceRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    设置竞品分析隐私偏好
    
    - **opt_out_benchmark**: 是否不参与行业基准计算
    """
    from app.database import UserRepository
    
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(current_user["id"])
    
    if not user:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"success": False, "message": "用户不存在"}
        )
    
    # 更新隐私偏好
    user.opt_out_benchmark = request.opt_out_benchmark
    db.commit()
    
    logger.info(f"用户ID {user.id} 更新竞品分析隐私设置为: opt_out_benchmark={request.opt_out_benchmark}")
    
    return {
        "success": True,
        "message": "竞品分析隐私设置已更新" if not request.opt_out_benchmark else "您已退出行业基准计算",
        "data": {
            "opt_out_benchmark": user.opt_out_benchmark
        }
    }


# ==================== 推荐系统增强路由 ====================

class ReferralMilestoneClaimRequest(BaseModel):
    """领取里程碑奖励请求"""
    pass  # 无需参数，自动领取最新可领取的里程碑


class ReferralAnonymousRequest(BaseModel):
    """设置排行榜匿名状态"""
    anonymous: bool = Field(..., description="是否在排行榜匿名显示")


@router.get("/referral/milestones")
async def get_referral_milestones(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取里程碑列表和当前进度
    """
    from app.database import UserRepository
    from app.services.referral import get_milestone_progress, MILESTONES
    
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(current_user["id"])
    
    if not user:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"success": False, "message": "用户不存在"}
        )
    
    progress = get_milestone_progress(user)
    
    return {
        "success": True,
        "message": "获取成功",
        "data": progress
    }


@router.post("/referral/claim-milestone")
async def claim_referral_milestone(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    领取里程碑奖励
    """
    from app.database import UserRepository
    from app.services.referral import claim_milestone_reward
    
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(current_user["id"])
    
    if not user:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"success": False, "message": "用户不存在"}
        )
    
    result = claim_milestone_reward(db, user)
    
    if result["success"]:
        return {
            "success": True,
            "message": result["message"],
            "data": result["reward"]
        }
    else:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"success": False, "message": result["message"]}
        )


@router.get("/referral/leaderboard")
async def get_referral_leaderboard(
    limit: int = 20,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取推荐排行榜（Top 20）
    """
    from app.services.referral import get_referral_leaderboard
    
    # 限制返回数量
    limit = min(max(1, limit), 100)
    
    leaderboard = get_referral_leaderboard(db, limit)
    
    return {
        "success": True,
        "message": "获取成功",
        "data": leaderboard
    }


@router.get("/referral/stats")
async def get_enhanced_referral_stats(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取详细推荐统计
    """
    from app.services.referral import get_enhanced_referral_stats
    
    stats = get_enhanced_referral_stats(db, current_user["id"])
    
    if "error" in stats:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"success": False, "message": stats["error"]}
        )
    
    return {
        "success": True,
        "message": "获取成功",
        "data": stats
    }


@router.post("/referral/anonymous")
async def set_referral_anonymous(
    request: ReferralAnonymousRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    设置是否在排行榜匿名显示
    """
    from app.database import UserRepository
    
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(current_user["id"])
    
    if not user:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"success": False, "message": "用户不存在"}
        )
    
    user.referral_anonymous = request.anonymous
    db.commit()
    
    logger.info(f"用户ID {user.id} 设置推荐排行榜匿名为: {request.anonymous}")
    
    return {
        "success": True,
        "message": "设置成功" if not request.anonymous else "您已切换到匿名模式",
        "data": {
            "referral_anonymous": user.referral_anonymous
        }
    }

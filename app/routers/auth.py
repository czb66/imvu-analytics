"""
认证路由 - 处理用户注册、登录、登出
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.auth import AuthService, get_current_user

router = APIRouter(prefix="/api/auth", tags=["认证"])


# ==================== 请求/响应模型 ====================

class RegisterRequest(BaseModel):
    """注册请求"""
    email: EmailStr = Field(..., description="邮箱地址")
    password: str = Field(..., min_length=8, description="密码（至少8位）")
    username: str = Field(None, max_length=100, description="用户名（可选）")


class LoginRequest(BaseModel):
    """登录请求"""
    email: EmailStr = Field(..., description="邮箱地址")
    password: str = Field(..., description="密码")
    remember_me: bool = Field(False, description="记住我")


class ChangePasswordRequest(BaseModel):
    """修改密码请求"""
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., min_length=8, description="新密码（至少8位）")


class UpdateUsernameRequest(BaseModel):
    """修改用户名请求"""
    username: str = Field(..., min_length=2, max_length=50, description="新用户名")


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

@router.post("/register", response_model=AuthResponse)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    用户注册
    
    - **email**: 邮箱地址（唯一）
    - **password**: 密码（至少8位）
    - **username**: 用户名（可选）
    """
    try:
        auth_service = AuthService(db)
        success, message, data = auth_service.register(
            email=request.email,
            password=request.password,
            username=request.username
        )
        
        if not success:
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
            content={"success": False, "message": f"注册失败: {str(e)}"}
        )


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    用户登录
    
    - **email**: 邮箱地址
    - **password**: 密码
    - **remember_me**: 记住我（延长Token有效期）
    """
    auth_service = AuthService(db)
    success, message, data = auth_service.login(
        email=request.email,
        password=request.password,
        remember_me=request.remember_me
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


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """
    用户登出
    
    注意：由于使用JWT无状态认证，后端不需要做任何处理
    客户端只需要删除本地存储的Token即可
    """
    return {
        "success": True,
        "message": "已安全退出"
    }


@router.get("/me", response_model=AuthResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    """
    获取当前登录用户信息
    """
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


@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    修改密码
    
    - **old_password**: 旧密码
    - **new_password**: 新密码（至少8位）
    """
    auth_service = AuthService(db)
    success, message = auth_service.change_password(
        user_id=current_user["id"],
        old_password=request.old_password,
        new_password=request.new_password
    )
    
    if not success:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"success": False, "message": message}
        )
    
    return {
        "success": True,
        "message": message
    }


@router.put("/username")
async def update_username(
    request: UpdateUsernameRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    修改用户名
    
    - **username**: 新用户名（2-50位）
    """
    auth_service = AuthService(db)
    success, message = auth_service.update_username(
        user_id=current_user["id"],
        new_username=request.username
    )
    
    if not success:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"success": False, "message": message}
        )
    
    return {
        "success": True,
        "message": message
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

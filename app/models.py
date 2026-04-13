"""
数据模型 - 定义数据结构
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class User(Base):
    """用户模型 - 用户注册和认证"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    username = Column(String(100), nullable=True)  # 可选的用户名
    is_active = Column(Boolean, default=True)  # 账户是否激活
    is_admin = Column(Boolean, default=False)  # 是否是管理员
    is_whitelisted = Column(Boolean, default=False)  # 是否在白名单中（跳过订阅检查）
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)  # 最后登录时间
    
    # 密码重置字段
    reset_token = Column(String(255), nullable=True)  # 重置令牌
    reset_token_expires = Column(DateTime, nullable=True)  # 重置令牌过期时间
    
    # Stripe订阅字段
    stripe_customer_id = Column(String(255), nullable=True, index=True)  # Stripe客户ID
    subscription_id = Column(String(255), nullable=True, index=True)  # 订阅ID
    subscription_status = Column(String(50), default='none')  # none/active/canceled/expired/past_due
    subscription_end_date = Column(DateTime, nullable=True)  # 订阅到期时间
    
    # 关联数据
    datasets = relationship("Dataset", back_populates="owner", cascade="all, delete-orphan")
    
    @property
    def is_subscribed(self) -> bool:
        """检查用户是否有有效订阅"""
        if self.subscription_status != 'active':
            return False
        if self.subscription_end_date and self.subscription_end_date < datetime.utcnow():
            return False
        return True
    
    def __repr__(self):
        return f"<User {self.email}>"


class Dataset(Base):
    """数据集模型 - 存储多个时期的数据"""
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)  # 如 "2024年1月"
    upload_time = Column(DateTime, default=datetime.utcnow)
    record_count = Column(Integer, default=0)  # 产品数量
    
    # 关联用户
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # nullable=True 兼容旧数据
    owner = relationship("User", back_populates="datasets")
    
    # 关联产品数据
    products = relationship("ProductData", back_populates="dataset", cascade="all, delete-orphan")


class ProductData(Base):
    """产品数据模型"""
    __tablename__ = "product_data"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(String(50), index=True, nullable=False)
    product_name = Column(String(500))
    price = Column(Float, default=0)
    profit = Column(Float, default=0)
    visible = Column(String(1), default='N')  # Y/N
    
    # 销售数据
    direct_sales = Column(Float, default=0)
    indirect_sales = Column(Float, default=0)
    promoted_sales = Column(Float, default=0)
    
    # 用户行为数据
    cart_adds = Column(Float, default=0)
    wishlist_adds = Column(Float, default=0)
    
    # 流量数据
    organic_impressions = Column(Float, default=0)
    paid_impressions = Column(Float, default=0)
    
    # 元数据
    upload_time = Column(DateTime, default=datetime.utcnow)
    data_date = Column(DateTime, nullable=True)  # 数据日期（可选）
    
    # 关联数据集
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=True)
    dataset = relationship("Dataset", back_populates="products")
    
    # 备注
    notes = Column(Text, nullable=True)


class ReportHistory(Base):
    """报告历史记录"""
    __tablename__ = "report_history"

    id = Column(Integer, primary_key=True, index=True)
    report_type = Column(String(50))  # daily, manual
    generated_at = Column(DateTime, default=datetime.utcnow)
    content_preview = Column(Text)  # 报告内容预览
    file_path = Column(String(500), nullable=True)  # 报告文件路径
    sent_to = Column(String(500), nullable=True)  # 邮件发送目标
    status = Column(String(20), default='pending')  # pending, completed, failed
    
    # 关联用户（可选）
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)


class SystemConfig(Base):
    """系统配置"""
    __tablename__ = "system_config"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, index=True)
    value = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PageView(Base):
    """页面访问统计模型"""
    __tablename__ = "page_views"

    id = Column(Integer, primary_key=True, index=True)
    path = Column(String(255), index=True)  # 访问路径
    ip_address = Column(String(50))  # 访问者IP（脱敏后存储）
    user_agent = Column(String(500))  # 浏览器信息
    referrer = Column(String(500), nullable=True)  # 来源页面
    created_at = Column(DateTime, default=datetime.utcnow, index=True)  # 访问时间

    def __repr__(self):
        return f"<PageView {self.path} at {self.created_at}>"

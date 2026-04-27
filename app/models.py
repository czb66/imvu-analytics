"""
数据模型 - 定义数据结构
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON
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
    
    # 免费试用期
    trial_end_date = Column(DateTime, nullable=True)  # 试用期结束时间（注册后7天）
    
    # 推荐系统
    referral_code = Column(String(20), unique=True, index=True, nullable=True)  # 用户的推荐码
    referred_by = Column(String(20), nullable=True)  # 被谁推荐（推荐人的 referral_code）
    
    # 防刷机制字段
    referral_reward_pending = Column(Boolean, default=False)  # 推荐奖励待发放（被推荐人需完成关键操作）
    referral_rewarded_at = Column(DateTime, nullable=True)  # 推荐奖励发放时间
    referral_suspended = Column(Boolean, default=False)  # 推荐码是否被暂停（异常检测触发）
    
    # Stripe订阅字段
    stripe_customer_id = Column(String(255), nullable=True, index=True)  # Stripe客户ID
    subscription_id = Column(String(255), nullable=True, index=True)  # 订阅ID
    subscription_status = Column(String(50), default='none')  # none/active/canceled/expired/past_due
    subscription_end_date = Column(DateTime, nullable=True)  # 订阅到期时间
    
    # 报告订阅设置
    report_preference = Column(String(20), default='weekly')  # daily/weekly/none, 新用户默认每周报告
    
    # 订阅到期提醒字段（防重复发送）
    reminder_3day_sent = Column(Boolean, default=False)  # 3天提醒已发
    reminder_1day_sent = Column(Boolean, default=False)  # 1天提醒已发
    reminder_recall_sent = Column(Boolean, default=False)  # 召回邮件已发
    last_reminder_sent = Column(DateTime, nullable=True)  # 最后提醒发送时间
    
    # 试用期到期提醒字段
    trial_reminder_3day_sent = Column(Boolean, default=False)  # 试用期3天提醒已发
    trial_reminder_1day_sent = Column(Boolean, default=False)  # 试用期1天提醒已发
    trial_reminder_recall_sent = Column(Boolean, default=False)  # 试用期召回邮件已发
    
    # 隐私设置 - 不参与行业基准计算
    opt_out_benchmark = Column(Boolean, default=False)  # 不参与行业基准计算
    
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
    
    @property
    def is_in_trial(self) -> bool:
        """检查用户是否在试用期内"""
        if not self.trial_end_date:
            return False
        return self.trial_end_date > datetime.utcnow()
    
    @property
    def has_premium_access(self) -> bool:
        """检查用户是否有高级功能访问权限（订阅或试用）"""
        # 白名单用户
        if self.is_whitelisted:
            return True
        # 有效订阅
        if self.is_subscribed:
            return True
        # 试用期内
        if self.is_in_trial:
            return True
        return False
    
    def __repr__(self):
        return f"<User {self.email}>"
    
    @property
    def is_referral_available(self) -> bool:
        """检查推荐码是否可用（未被暂停且未过期）"""
        return not self.referral_suspended


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


class PromoCardStat(Base):
    """推广卡片生成统计模型"""
    __tablename__ = "promo_card_stats"

    id = Column(Integer, primary_key=True, index=True)
    
    # 基本信息
    card_title = Column(String(255))  # 卡片标题
    card_subtitle = Column(String(255))  # 卡片副标题
    card_intro = Column(Text)  # 介绍文字
    card_footer = Column(Text)  # 底部文字
    
    # 样式设置
    style = Column(String(50))  # grid/list/card/compact/featured
    color = Column(String(50))  # purple/gold/blue/red/green
    
    # 产品信息
    product_count = Column(Integer, default=0)  # 产品数量
    products_json = Column(Text)  # 产品完整信息（JSON格式）
    
    # 统计信息
    total_clicks = Column(Integer, default=0)  # 总点击次数
    last_click_at = Column(DateTime, nullable=True)  # 最后点击时间
    
    # 用户信息
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # 关联用户（可选）
    session_id = Column(String(100), nullable=True)  # 会话ID（匿名用户）
    ip_address = Column(String(50), nullable=True)  # IP地址
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<PromoCardStat {self.card_title} - {self.style} at {self.created_at}>"


class PromoCardClick(Base):
    """推广卡片点击统计模型"""
    __tablename__ = "promo_card_clicks"

    id = Column(Integer, primary_key=True, index=True)
    
    # 关联卡片
    stat_id = Column(Integer, ForeignKey("promo_card_stats.id"), index=True)
    product_index = Column(Integer, default=0)  # 产品序号（第几个产品）
    product_name = Column(String(255))  # 产品名称
    original_link = Column(String(500))  # 原始链接
    
    # 点击者信息
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    referrer = Column(String(500), nullable=True)  # 来源页面
    
    # 时间戳
    clicked_at = Column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<PromoCardClick stat_id={self.stat_id} product={self.product_name}>"


class UserActivity(Base):
    """用户行为追踪模型 - 记录用户在平台上的关键操作"""
    __tablename__ = "user_activities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    
    # 行为类型
    action = Column(String(50), nullable=False, index=True)
    # 可选值: login, logout, register, upload, view_dashboard, view_diagnosis, 
    #         view_compare, view_insights, generate_report, export_pdf, 
    #         create_promo_card, subscribe, cancel_subscription
    
    # 资源信息
    resource_type = Column(String(50), nullable=True)  # dataset, report, promo_card
    resource_id = Column(Integer, nullable=True)
    
    # 额外元数据（不记录敏感信息如密码、完整IP等）
    extra_data = Column(JSON, nullable=True)  # 如设备信息、浏览器类型等
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # 关联
    user = relationship("User", backref="activities")

    def __repr__(self):
        return f"<UserActivity user_id={self.user_id} action={self.action}>"


class IndustryBenchmark(Base):
    """行业基准数据模型 - 存储聚合后的行业统计数据"""
    __tablename__ = "industry_benchmarks"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(100), nullable=False, index=True)  # 产品类别
    metric = Column(String(50), nullable=False)  # 指标名：avg_sales, median_sales, avg_profit_margin 等
    value = Column(Float, nullable=False)  # 指标值
    percentile_25 = Column(Float, nullable=True)  # 25分位
    percentile_50 = Column(Float, nullable=True)  # 50分位（中位数）
    percentile_75 = Column(Float, nullable=True)  # 75分位
    percentile_90 = Column(Float, nullable=True)  # 90分位
    sample_size = Column(Integer, default=0)  # 样本数
    is_sufficient = Column(Boolean, default=False)  # 样本是否足够（>=5）
    updated_at = Column(DateTime, default=datetime.utcnow)  # 更新时间

    def __repr__(self):
        return f"<IndustryBenchmark category={self.category} metric={self.metric}>"

"""
数据模型 - 定义数据结构
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Dataset(Base):
    """数据集模型 - 存储多个时期的数据"""
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)  # 如 "2024年1月"
    upload_time = Column(DateTime, default=datetime.utcnow)
    record_count = Column(Integer, default=0)  # 产品数量
    
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


class SystemConfig(Base):
    """系统配置"""
    __tablename__ = "system_config"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, index=True)
    value = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

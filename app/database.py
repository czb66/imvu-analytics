"""
数据库管理 - SQLite/PostgreSQL数据库操作
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
from typing import Generator
import config

from app.models import Base, ProductData, ReportHistory, SystemConfig, Dataset

# 数据库引擎配置
if "sqlite" in config.DATABASE_URL:
    # SQLite 配置
    engine = create_engine(
        config.DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=config.DEBUG
    )
else:
    # PostgreSQL 配置
    engine = create_engine(
        config.DATABASE_URL,
        poolclass=QueuePool,
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=1800,
        echo=config.DEBUG
    )

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """初始化数据库，创建所有表"""
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """获取数据库会话的依赖项"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context():
    """上下文管理器方式的数据库会话"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


class ProductDataRepository:
    """产品数据仓储类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def bulk_insert(self, products: list, dataset_id: int = None) -> int:
        """批量插入产品数据"""
        for product in products:
            db_product = ProductData(**product)
            if dataset_id:
                db_product.dataset_id = dataset_id
            self.db.add(db_product)
        self.db.commit()
        return len(products)
    
    def bulk_insert_with_dataset(self, products: list, dataset_id: int) -> int:
        """批量插入产品数据到指定数据集（先清空该数据集的旧数据）"""
        # 删除该数据集的旧数据
        self.db.query(ProductData).filter(ProductData.dataset_id == dataset_id).delete()
        self.db.commit()
        
        # 插入新产品数据
        for product in products:
            db_product = ProductData(**product)
            db_product.dataset_id = dataset_id
            self.db.add(db_product)
        self.db.commit()
        return len(products)
    
    def get_all(self) -> list:
        """获取所有产品数据（不区分数据集）"""
        return self.db.query(ProductData).filter(ProductData.dataset_id == None).all()
    
    def get_by_dataset(self, dataset_id: int) -> list:
        """获取指定数据集的产品数据"""
        return self.db.query(ProductData).filter(ProductData.dataset_id == dataset_id).all()
    
    def get_by_id(self, product_id: str) -> ProductData:
        """根据产品ID获取数据"""
        return self.db.query(ProductData).filter(
            ProductData.product_id == product_id
        ).first()
    
    def get_visible_products(self, visible: str = 'Y') -> list:
        """获取可见/不可见产品"""
        return self.db.query(ProductData).filter(
            ProductData.visible == visible
        ).all()
    
    def get_top_products(self, limit: int = 10, sort_by: str = 'profit', dataset_id: int = None) -> list:
        """获取Top产品"""
        query = self.db.query(ProductData)
        if dataset_id is not None:
            query = query.filter(ProductData.dataset_id == dataset_id)
        column = getattr(ProductData, sort_by, ProductData.profit)
        return query.order_by(column.desc()).limit(limit).all()
    
    def get_bottom_products(self, limit: int = 10, sort_by: str = 'profit', dataset_id: int = None) -> list:
        """获取Bottom产品"""
        query = self.db.query(ProductData)
        if dataset_id is not None:
            query = query.filter(ProductData.dataset_id == dataset_id)
        column = getattr(ProductData, sort_by, ProductData.profit)
        return query.order_by(column.asc()).limit(limit).all()
    
    def count_by_dataset(self, dataset_id: int) -> int:
        """统计指定数据集的产品数量"""
        return self.db.query(ProductData).filter(ProductData.dataset_id == dataset_id).count()


class DatasetRepository:
    """数据集仓储类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, name: str, record_count: int = 0) -> Dataset:
        """创建新数据集"""
        dataset = Dataset(name=name, record_count=record_count)
        self.db.add(dataset)
        self.db.commit()
        self.db.refresh(dataset)
        return dataset
    
    def get_all(self) -> list:
        """获取所有数据集"""
        return self.db.query(Dataset).order_by(Dataset.upload_time.desc()).all()
    
    def get_by_id(self, dataset_id: int) -> Dataset:
        """根据ID获取数据集"""
        return self.db.query(Dataset).filter(Dataset.id == dataset_id).first()
    
    def update_record_count(self, dataset_id: int, count: int):
        """更新数据集的产品数量"""
        dataset = self.get_by_id(dataset_id)
        if dataset:
            dataset.record_count = count
            self.db.commit()
    
    def delete(self, dataset_id: int):
        """删除数据集及其关联的产品数据"""
        # 级联删除会在数据库层面处理
        dataset = self.get_by_id(dataset_id)
        if dataset:
            self.db.delete(dataset)
            self.db.commit()
    
    def get_latest(self, limit: int = 10) -> list:
        """获取最新的N个数据集"""
        return self.db.query(Dataset).order_by(Dataset.upload_time.desc()).limit(limit).all()


class ReportHistoryRepository:
    """报告历史仓储类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, report_data: dict) -> ReportHistory:
        """创建报告记录"""
        report = ReportHistory(**report_data)
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        return report
    
    def get_recent(self, limit: int = 10) -> list:
        """获取最近的报告"""
        return self.db.query(ReportHistory).order_by(
            ReportHistory.generated_at.desc()
        ).limit(limit).all()
    
    def update_status(self, report_id: int, status: str, **kwargs):
        """更新报告状态"""
        report = self.db.query(ReportHistory).filter(
            ReportHistory.id == report_id
        ).first()
        if report:
            report.status = status
            for key, value in kwargs.items():
                if hasattr(report, key):
                    setattr(report, key, value)
            self.db.commit()

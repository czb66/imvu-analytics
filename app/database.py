"""
数据库管理 - SQLite/PostgreSQL数据库操作
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
from typing import Generator
from datetime import datetime
import config

from app.models import Base, ProductData, ReportHistory, SystemConfig, Dataset, User, PageView, PromoCardStat, PromoCardClick

# 数据库引擎配置
if "sqlite" in config.DATABASE_URL:
    # SQLite 配置
    engine = create_engine(
        config.DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=config.DEBUG
    )
else:
    # PostgreSQL/Neon 配置
    # Neon 需要 SSL 连接
    connect_args = {"sslmode": "require"} if "neon.tech" in config.DATABASE_URL else {}
    
    engine = create_engine(
        config.DATABASE_URL,
        poolclass=QueuePool,
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=1800,
        pool_pre_ping=True,  # 检查连接是否有效
        connect_args=connect_args,
        echo=config.DEBUG
    )

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """初始化数据库，创建所有表并执行迁移"""
    import logging
    logger = logging.getLogger(__name__)
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    
    # 执行数据库迁移（添加缺失的列）
    _run_migrations(logger)


def _run_migrations(logger):
    """执行数据库迁移 - 添加缺失的列"""
    from sqlalchemy import text, inspect
    
    try:
        with engine.connect() as conn:
            inspector = inspect(engine)
            table_names = inspector.get_table_names()
            
            # 检查 users 表是否存在
            if 'users' not in table_names:
                logger.info("users 表不存在，跳过迁移")
                return
            
            # 获取 users 表现有的列
            existing_columns = [col['name'] for col in inspector.get_columns('users')]
            
            # 迁移 1: 添加 is_whitelisted 列
            if 'is_whitelisted' not in existing_columns:
                logger.info("正在添加 is_whitelisted 列到 users 表...")
                if "sqlite" in config.DATABASE_URL:
                    conn.execute(text("ALTER TABLE users ADD COLUMN is_whitelisted BOOLEAN DEFAULT 0"))
                else:
                    conn.execute(text("ALTER TABLE users ADD COLUMN is_whitelisted BOOLEAN DEFAULT FALSE"))
                conn.commit()
                logger.info("is_whitelisted 列添加成功")
            
            # 迁移 2: 添加 trial_end_date 列（7天免费试用）
            if 'trial_end_date' not in existing_columns:
                logger.info("正在添加 trial_end_date 列到 users 表...")
                conn.execute(text("ALTER TABLE users ADD COLUMN trial_end_date TIMESTAMP"))
                conn.commit()
                logger.info("trial_end_date 列添加成功")
            
            # 迁移 3: 检查 promo_card_stats 表
            if 'promo_card_stats' in table_names:
                promo_card_columns = [col['name'] for col in inspector.get_columns('promo_card_stats')]
                
                # 所有可能缺失的列
                columns_to_add = [
                    ('card_title', 'VARCHAR(255)'),
                    ('card_subtitle', 'VARCHAR(255)'),
                    ('card_intro', 'TEXT'),
                    ('card_footer', 'TEXT'),
                    ('style', 'VARCHAR(50)'),
                    ('color', 'VARCHAR(50)'),
                    ('product_count', 'INTEGER DEFAULT 0'),
                    ('products_json', 'TEXT'),
                    ('total_clicks', 'INTEGER DEFAULT 0'),
                    ('last_click_at', 'TIMESTAMP'),
                    ('user_id', 'INTEGER'),
                    ('session_id', 'VARCHAR(100)'),
                    ('ip_address', 'VARCHAR(50)'),
                    ('created_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
                    ('updated_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
                ]
                
                for col_name, col_type in columns_to_add:
                    if col_name not in promo_card_columns:
                        logger.info(f"正在添加 {col_name} 列到 promo_card_stats 表...")
                        try:
                            conn.execute(text(f"ALTER TABLE promo_card_stats ADD COLUMN {col_name} {col_type}"))
                            conn.commit()
                            logger.info(f"{col_name} 列添加成功")
                        except Exception as col_err:
                            logger.warning(f"添加 {col_name} 列失败（可能已存在）: {col_err}")
            
            # 迁移 3: 检查 promo_card_clicks 表
            if 'promo_card_clicks' not in table_names:
                logger.info("promo_card_clicks 表不存在，将由 create_all 创建")
            
            logger.info("数据库迁移完成")
            
    except Exception as e:
        logger.warning(f"数据库迁移失败（可能已存在）: {e}")


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


class UserRepository:
    """用户仓储类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, email: str, password_hash: str, username: str = None) -> User:
        """创建新用户，自动赠送7天Pro试用"""
        from datetime import timedelta
        
        # 设置试用期：注册后7天
        trial_end = datetime.utcnow() + timedelta(days=7)
        
        user = User(
            email=email,
            password_hash=password_hash,
            username=username,
            trial_end_date=trial_end  # 赠送7天Pro试用
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def get_by_email(self, email: str) -> User:
        """根据邮箱获取用户"""
        return self.db.query(User).filter(User.email == email.lower()).first()
    
    def get_by_id(self, user_id: int) -> User:
        """根据ID获取用户"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def email_exists(self, email: str) -> bool:
        """检查邮箱是否已注册"""
        return self.db.query(User).filter(User.email == email.lower()).first() is not None
    
    def update_password(self, user_id: int, new_password_hash: str):
        """更新用户密码"""
        user = self.get_by_id(user_id)
        if user:
            user.password_hash = new_password_hash
            self.db.commit()
    
    def update_username(self, user_id: int, new_username: str):
        """更新用户名"""
        user = self.get_by_id(user_id)
        if user:
            user.username = new_username
            self.db.commit()
    
    def update_last_login(self, user_id: int):
        """更新最后登录时间"""
        user = self.get_by_id(user_id)
        if user:
            user.last_login = datetime.utcnow()
            self.db.commit()
    
    def delete(self, user_id: int):
        """删除用户"""
        user = self.get_by_id(user_id)
        if user:
            self.db.delete(user)
            self.db.commit()
    
    def set_reset_token(self, email: str, token: str, expires_at: datetime):
        """设置用户密码重置令牌"""
        user = self.get_by_email(email)
        if user:
            user.reset_token = token
            user.reset_token_expires = expires_at
            self.db.commit()
            return True
        return False
    
    def verify_reset_token(self, token: str) -> User:
        """验证重置令牌，返回用户如果有效"""
        return self.db.query(User).filter(
            User.reset_token == token,
            User.reset_token_expires > datetime.utcnow()
        ).first()
    
    def reset_password(self, token: str, new_password_hash: str) -> tuple:
        """
        使用令牌重置密码
        Returns: (success, message)
        """
        user = self.verify_reset_token(token)
        if not user:
            return False, "重置链接已过期或无效"
        
        user.password_hash = new_password_hash
        user.reset_token = None
        user.reset_token_expires = None
        self.db.commit()
        return True, "密码重置成功"


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
    
    def get_all(self, user_id: int = None) -> list:
        """获取最新数据集的产品数据（用于 Dashboard 显示）"""
        # 获取最新上传的数据集（按用户过滤）
        latest_dataset = self._get_latest_dataset_for_user(user_id)
        
        if latest_dataset:
            # 返回最新数据集的数据
            return self.db.query(ProductData).filter(
                ProductData.dataset_id == latest_dataset.id
            ).all()
        
        # 兼容旧逻辑：如果没有数据集，返回 dataset_id == None 的数据
        # 如果有user_id，则返回该用户的数据
        query = self.db.query(ProductData)
        if user_id:
            # 获取该用户的数据集
            user_datasets = self.db.query(Dataset).filter(Dataset.user_id == user_id).all()
            dataset_ids = [d.id for d in user_datasets]
            if dataset_ids:
                query = query.filter(ProductData.dataset_id.in_(dataset_ids))
            else:
                return []
        else:
            query = query.filter(ProductData.dataset_id == None)
        return query.all()
    
    def _get_latest_dataset_for_user(self, user_id: int = None):
        """获取用户最新的数据集"""
        query = self.db.query(Dataset)
        if user_id is not None:
            query = query.filter(Dataset.user_id == user_id)
        return query.order_by(Dataset.upload_time.desc()).first()
    
    def get_by_dataset(self, dataset_id: int) -> list:
        """获取指定数据集的产品数据"""
        return self.db.query(ProductData).filter(ProductData.dataset_id == dataset_id).all()
    
    def get_by_id(self, product_id: str) -> ProductData:
        """根据产品ID获取数据"""
        return self.db.query(ProductData).filter(
            ProductData.product_id == product_id
        ).first()
    
    def get_visible_products(self, visible: str = 'Y', user_id: int = None) -> list:
        """获取可见/不可见产品（最新数据集）"""
        # 获取最新上传的数据集
        latest_dataset = self._get_latest_dataset_for_user(user_id)
        
        query = self.db.query(ProductData)
        
        if latest_dataset:
            query = query.filter(
                ProductData.dataset_id == latest_dataset.id,
                ProductData.visible == visible
            )
        else:
            # 兼容旧逻辑
            if user_id:
                # 获取该用户的数据集
                user_datasets = self.db.query(Dataset).filter(Dataset.user_id == user_id).all()
                dataset_ids = [d.id for d in user_datasets]
                if dataset_ids:
                    query = query.filter(
                        ProductData.dataset_id.in_(dataset_ids),
                        ProductData.visible == visible
                    )
                else:
                    return []
            else:
                query = query.filter(
                    ProductData.dataset_id == None,
                    ProductData.visible == visible
                )
        
        return query.all()
    
    def get_top_products(self, limit: int = 10, sort_by: str = 'profit', dataset_id: int = None, user_id: int = None) -> list:
        """获取Top产品"""
        query = self.db.query(ProductData)
        
        # 按数据集过滤
        if dataset_id is not None:
            query = query.filter(ProductData.dataset_id == dataset_id)
        elif user_id is not None:
            # 获取该用户最新的数据集
            latest_dataset = self._get_latest_dataset_for_user(user_id)
            if latest_dataset:
                query = query.filter(ProductData.dataset_id == latest_dataset.id)
            else:
                return []
        
        column = getattr(ProductData, sort_by, ProductData.profit)
        return query.order_by(column.desc()).limit(limit).all()
    
    def get_bottom_products(self, limit: int = 10, sort_by: str = 'profit', dataset_id: int = None, user_id: int = None) -> list:
        """获取Bottom产品"""
        query = self.db.query(ProductData)
        
        if dataset_id is not None:
            query = query.filter(ProductData.dataset_id == dataset_id)
        elif user_id is not None:
            latest_dataset = self._get_latest_dataset_for_user(user_id)
            if latest_dataset:
                query = query.filter(ProductData.dataset_id == latest_dataset.id)
            else:
                return []
        
        column = getattr(ProductData, sort_by, ProductData.profit)
        return query.order_by(column.asc()).limit(limit).all()
    
    def count_by_dataset(self, dataset_id: int) -> int:
        """统计指定数据集的产品数量"""
        return self.db.query(ProductData).filter(ProductData.dataset_id == dataset_id).count()


class DatasetRepository:
    """数据集仓储类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, name: str, record_count: int = 0, user_id: int = None) -> Dataset:
        """创建新数据集"""
        dataset = Dataset(name=name, record_count=record_count, user_id=user_id)
        self.db.add(dataset)
        self.db.commit()
        self.db.refresh(dataset)
        return dataset
    
    def get_all(self, user_id: int = None) -> list:
        """获取所有数据集"""
        query = self.db.query(Dataset)
        if user_id is not None:
            query = query.filter(Dataset.user_id == user_id)
        return query.order_by(Dataset.upload_time.desc()).all()
    
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
        dataset = self.get_by_id(dataset_id)
        if dataset:
            self.db.delete(dataset)
            self.db.commit()
    
    def get_latest(self, limit: int = 10, user_id: int = None) -> list:
        """获取最新的N个数据集"""
        query = self.db.query(Dataset)
        if user_id is not None:
            query = query.filter(Dataset.user_id == user_id)
        return query.order_by(Dataset.upload_time.desc()).limit(limit).all()


class ReportHistoryRepository:
    """报告历史仓储类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, report_data: dict, user_id: int = None) -> ReportHistory:
        """创建报告记录"""
        report = ReportHistory(**report_data, user_id=user_id)
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        return report
    
    def get_recent(self, limit: int = 10, user_id: int = None) -> list:
        """获取最近的报告"""
        query = self.db.query(ReportHistory)
        if user_id is not None:
            query = query.filter(ReportHistory.user_id == user_id)
        return query.order_by(
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

    def get_by_reset_token(self, token: str) -> User:
        """根据重置令牌获取用户"""
        return self.db.query(User).filter(User.reset_token == token).first()

    def get_by_reset_token_hash(self, token_hash: str) -> User:
        """根据重置令牌哈希获取用户"""
        return self.db.query(User).filter(User.reset_token == token_hash).first()

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

from app.models import Base, ProductData, ReportHistory, SystemConfig, Dataset, User, PageView, PromoCardStat, PromoCardClick, UserActivity, IndustryBenchmark, BlogPost

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
    """执行数据库迁移 - 添加缺失的列
    
    核心原则：每个迁移步骤独立 try/except，一个失败不影响后续迁移。
    这是因为之前的单 try/except 导致某个迁移报错后，后续所有迁移全部跳过，
    造成生产数据库大量列缺失。
    """
    from sqlalchemy import text, inspect
    
    is_sqlite = "sqlite" in config.DATABASE_URL
    
    def _add_column(conn, table, col_name, col_type, existing_cols):
        """安全添加列，已存在则跳过，失败则记录但不中断"""
        if col_name in existing_cols:
            return existing_cols
        try:
            conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {col_name} {col_type}"))
            conn.commit()
            logger.info(f"{table}.{col_name} 列添加成功")
            # 刷新列列表
            return existing_cols + [col_name]
        except Exception as e:
            logger.warning(f"添加 {table}.{col_name} 列失败: {e}")
            conn.rollback()
            return existing_cols
    
    def _create_table(conn, table_name, sqlite_ddl, postgres_ddl, table_names):
        """安全创建表，已存在则跳过"""
        if table_name in table_names:
            return table_names
        try:
            conn.execute(text(sqlite_ddl if is_sqlite else postgres_ddl))
            conn.commit()
            logger.info(f"{table_name} 表创建成功")
            return table_names + [table_name]
        except Exception as e:
            logger.warning(f"创建 {table_name} 表失败: {e}")
            conn.rollback()
            return table_names
    
    try:
        with engine.connect() as conn:
            inspector = inspect(engine)
            table_names = inspector.get_table_names()
            
            # 检查 users 表是否存在
            if 'users' not in table_names:
                logger.info("users 表不存在，跳过迁移")
                return
            
            # 获取 users 表现有的列（会在迁移过程中动态更新）
            existing_columns = [col['name'] for col in inspector.get_columns('users')]
            logger.info(f"users 表当前有 {len(existing_columns)} 列: {existing_columns}")
            
            # ====== 迁移 1: 添加 is_whitelisted 列 ======
            existing_columns = _add_column(conn, 'users', 'is_whitelisted',
                'BOOLEAN DEFAULT 0' if is_sqlite else 'BOOLEAN DEFAULT FALSE',
                existing_columns)
            
            # ====== 迁移 2: 添加 trial_end_date 列 ======
            existing_columns = _add_column(conn, 'users', 'trial_end_date', 'TIMESTAMP', existing_columns)
            
            # ====== 迁移 3: 添加推荐系统字段 ======
            existing_columns = _add_column(conn, 'users', 'referral_code', 'VARCHAR(20)', existing_columns)
            existing_columns = _add_column(conn, 'users', 'referred_by', 'VARCHAR(20)', existing_columns)
            
            # 为已有用户生成推荐码
            try:
                if 'referral_code' in existing_columns:
                    users = conn.execute(text("SELECT id, referral_code FROM users WHERE referral_code IS NULL")).fetchall()
                    if users:
                        import secrets
                        import string
                        chars = string.ascii_uppercase + string.digits
                        chars = chars.replace('O', '').replace('0', '').replace('I', '').replace('1', '').replace('L', '')
                        for user_id, _ in users:
                            code = ''.join(secrets.choice(chars) for _ in range(8))
                            while conn.execute(text("SELECT id FROM users WHERE referral_code = :code"), {"code": code}).fetchone():
                                code = ''.join(secrets.choice(chars) for _ in range(8))
                            conn.execute(text("UPDATE users SET referral_code = :code WHERE id = :id"), {"code": code, "id": user_id})
                        conn.commit()
                        logger.info(f"已为 {len(users)} 个用户生成推荐码")
            except Exception as e:
                logger.warning(f"生成推荐码失败: {e}")
                conn.rollback()
            
            # ====== 迁移 4: 检查 promo_card_stats 表 ======
            try:
                if 'promo_card_stats' in table_names:
                    promo_card_columns = [col['name'] for col in inspector.get_columns('promo_card_stats')]
                    columns_to_add = [
                        ('card_title', 'VARCHAR(255)'), ('card_subtitle', 'VARCHAR(255)'),
                        ('card_intro', 'TEXT'), ('card_footer', 'TEXT'),
                        ('style', 'VARCHAR(50)'), ('color', 'VARCHAR(50)'),
                        ('product_count', 'INTEGER DEFAULT 0'), ('products_json', 'TEXT'),
                        ('total_clicks', 'INTEGER DEFAULT 0'), ('last_click_at', 'TIMESTAMP'),
                        ('user_id', 'INTEGER'), ('session_id', 'VARCHAR(100)'),
                        ('ip_address', 'VARCHAR(50)'),
                        ('created_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
                        ('updated_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
                    ]
                    for col_name, col_type in columns_to_add:
                        promo_card_columns = _add_column(conn, 'promo_card_stats', col_name, col_type, promo_card_columns)
            except Exception as e:
                logger.warning(f"promo_card_stats 迁移失败: {e}")
                conn.rollback()
            
            # ====== 迁移 5: 创建 user_activities 表 ======
            table_names = _create_table(conn, 'user_activities',
                """CREATE TABLE user_activities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    action VARCHAR(50) NOT NULL,
                    resource_type VARCHAR(50),
                    resource_id INTEGER,
                    extra_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )""",
                """CREATE TABLE user_activities (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id),
                    action VARCHAR(50) NOT NULL,
                    resource_type VARCHAR(50),
                    resource_id INTEGER,
                    extra_data JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )""",
                table_names)
            # 索引
            try:
                for idx in ['ix_user_activities_user_id', 'ix_user_activities_action', 'ix_user_activities_created_at']:
                    conn.execute(text(f"CREATE INDEX IF NOT EXISTS {idx} ON user_activities ({idx.replace('ix_user_activities_', '')})"))
                conn.commit()
            except Exception as e:
                logger.warning(f"user_activities 索引创建失败（可能已存在）: {e}")
                conn.rollback()
            
            # ====== 迁移 6: 添加 report_preference 字段 ======
            existing_columns = _add_column(conn, 'users', 'report_preference', "VARCHAR(20) DEFAULT 'weekly'", existing_columns)
            
            # ====== 迁移 7: 添加订阅到期提醒字段 ======
            reminder_fields = [
                ('reminder_3day_sent', 'BOOLEAN DEFAULT 0' if is_sqlite else 'BOOLEAN DEFAULT FALSE'),
                ('reminder_1day_sent', 'BOOLEAN DEFAULT 0' if is_sqlite else 'BOOLEAN DEFAULT FALSE'),
                ('reminder_recall_sent', 'BOOLEAN DEFAULT 0' if is_sqlite else 'BOOLEAN DEFAULT FALSE'),
                ('trial_reminder_3day_sent', 'BOOLEAN DEFAULT 0' if is_sqlite else 'BOOLEAN DEFAULT FALSE'),
                ('trial_reminder_1day_sent', 'BOOLEAN DEFAULT 0' if is_sqlite else 'BOOLEAN DEFAULT FALSE'),
                ('trial_reminder_recall_sent', 'BOOLEAN DEFAULT 0' if is_sqlite else 'BOOLEAN DEFAULT FALSE'),
            ]
            for col_name, col_type in reminder_fields:
                existing_columns = _add_column(conn, 'users', col_name, col_type, existing_columns)
            
            # ====== 迁移 8: 添加 last_reminder_sent 字段 ======
            existing_columns = _add_column(conn, 'users', 'last_reminder_sent', 'TIMESTAMP', existing_columns)
            
            # ====== 迁移 9: 添加防刷机制字段 ======
            antifraud_fields = [
                ('referral_reward_pending', 'BOOLEAN DEFAULT 0' if is_sqlite else 'BOOLEAN DEFAULT FALSE'),
                ('referral_rewarded_at', 'TIMESTAMP'),
                ('referral_suspended', 'BOOLEAN DEFAULT 0' if is_sqlite else 'BOOLEAN DEFAULT FALSE'),
            ]
            for col_name, col_type in antifraud_fields:
                existing_columns = _add_column(conn, 'users', col_name, col_type, existing_columns)
            
            # ====== 迁移 10: 添加 opt_out_benchmark 字段 ======
            existing_columns = _add_column(conn, 'users', 'opt_out_benchmark',
                'BOOLEAN DEFAULT 0' if is_sqlite else 'BOOLEAN DEFAULT FALSE',
                existing_columns)
            
            # ====== 迁移 11: 创建 industry_benchmarks 表 ======
            table_names = _create_table(conn, 'industry_benchmarks',
                """CREATE TABLE industry_benchmarks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category VARCHAR(100) NOT NULL,
                    metric VARCHAR(50) NOT NULL,
                    value FLOAT NOT NULL,
                    percentile_25 FLOAT,
                    percentile_50 FLOAT,
                    percentile_75 FLOAT,
                    percentile_90 FLOAT,
                    sample_size INTEGER DEFAULT 0,
                    is_sufficient BOOLEAN DEFAULT 0,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )""",
                """CREATE TABLE industry_benchmarks (
                    id SERIAL PRIMARY KEY,
                    category VARCHAR(100) NOT NULL,
                    metric VARCHAR(50) NOT NULL,
                    value FLOAT NOT NULL,
                    percentile_25 FLOAT,
                    percentile_50 FLOAT,
                    percentile_75 FLOAT,
                    percentile_90 FLOAT,
                    sample_size INTEGER DEFAULT 0,
                    is_sufficient BOOLEAN DEFAULT FALSE,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )""",
                table_names)
            try:
                conn.execute(text("CREATE INDEX IF NOT EXISTS ix_industry_benchmarks_category ON industry_benchmarks (category)"))
                conn.commit()
            except Exception as e:
                logger.warning(f"industry_benchmarks 索引创建失败: {e}")
                conn.rollback()
            
            # ====== 迁移 12: 添加 onboarding 引导流程字段 ======
            onboarding_fields = [
                ('onboarding_step', 'INTEGER DEFAULT 0'),
                ('onboarding_completed_at', 'TIMESTAMP'),
            ]
            for col_name, col_type in onboarding_fields:
                existing_columns = _add_column(conn, 'users', col_name, col_type, existing_columns)
            
            # ====== 迁移 13: 添加推荐里程碑字段 ======
            milestone_fields = [
                ('referral_milestone', 'INTEGER DEFAULT 0'),
                ('referral_milestone_claimed', 'BOOLEAN DEFAULT 0' if is_sqlite else 'BOOLEAN DEFAULT FALSE'),
                ('referral_anonymous', 'BOOLEAN DEFAULT 0' if is_sqlite else 'BOOLEAN DEFAULT FALSE'),
            ]
            for col_name, col_type in milestone_fields:
                existing_columns = _add_column(conn, 'users', col_name, col_type, existing_columns)
            
            # ====== 迁移 14: 创建 user_feedback 表 ======
            table_names = _create_table(conn, 'user_feedback',
                """CREATE TABLE user_feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    nps_score INTEGER,
                    feedback_type VARCHAR(20),
                    content TEXT,
                    page_url VARCHAR(500),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )""",
                """CREATE TABLE user_feedback (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id),
                    nps_score INTEGER,
                    feedback_type VARCHAR(20),
                    content TEXT,
                    page_url VARCHAR(500),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )""",
                table_names)
            try:
                for idx in ['ix_user_feedback_user_id', 'ix_user_feedback_created_at']:
                    conn.execute(text(f"CREATE INDEX IF NOT EXISTS {idx} ON user_feedback ({idx.replace('ix_user_feedback_', '')})"))
                conn.commit()
            except Exception as e:
                logger.warning(f"user_feedback 索引创建失败: {e}")
                conn.rollback()
            
            # ====== 迁移 15: 创建 blog_posts 表 ======
            table_names = _create_table(conn, 'blog_posts',
                """CREATE TABLE blog_posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    slug VARCHAR(200) UNIQUE NOT NULL,
                    title_en VARCHAR(200) NOT NULL,
                    title_zh VARCHAR(200),
                    title_fr VARCHAR(200),
                    content_en TEXT NOT NULL,
                    content_zh TEXT,
                    content_fr TEXT,
                    excerpt_en VARCHAR(500),
                    excerpt_zh VARCHAR(500),
                    excerpt_fr VARCHAR(500),
                    category VARCHAR(50),
                    cover_image VARCHAR(500),
                    meta_title VARCHAR(200),
                    meta_description VARCHAR(500),
                    is_published BOOLEAN DEFAULT 0,
                    published_at TIMESTAMP,
                    author VARCHAR(100) DEFAULT 'IMVU Analytics Team',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    view_count INTEGER DEFAULT 0,
                    is_featured BOOLEAN DEFAULT 0
                )""",
                """CREATE TABLE blog_posts (
                    id SERIAL PRIMARY KEY,
                    slug VARCHAR(200) UNIQUE NOT NULL,
                    title_en VARCHAR(200) NOT NULL,
                    title_zh VARCHAR(200),
                    title_fr VARCHAR(200),
                    content_en TEXT NOT NULL,
                    content_zh TEXT,
                    content_fr TEXT,
                    excerpt_en VARCHAR(500),
                    excerpt_zh VARCHAR(500),
                    excerpt_fr VARCHAR(500),
                    category VARCHAR(50),
                    cover_image VARCHAR(500),
                    meta_title VARCHAR(200),
                    meta_description VARCHAR(500),
                    is_published BOOLEAN DEFAULT FALSE,
                    published_at TIMESTAMP,
                    author VARCHAR(100) DEFAULT 'IMVU Analytics Team',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    view_count INTEGER DEFAULT 0,
                    is_featured BOOLEAN DEFAULT FALSE
                )""",
                table_names)
            try:
                for col in ['slug', 'category', 'is_published', 'view_count']:
                    conn.execute(text(f"CREATE INDEX IF NOT EXISTS ix_blog_posts_{col} ON blog_posts ({col})"))
                conn.commit()
            except Exception as e:
                logger.warning(f"blog_posts 索引创建失败: {e}")
                conn.rollback()
            
            # ====== 迁移 16: 添加催款/支付失败挽回字段 ======
            dunning_columns = [
                ('dunning_status', "VARCHAR(20) DEFAULT 'active'"),
                ('dunning_started_at', 'TIMESTAMP'),
                ('payment_failed_count', 'INTEGER DEFAULT 0'),
                ('payment_retry_at', 'TIMESTAMP'),
                ('churn_risk_level', "VARCHAR(10) DEFAULT 'low'"),
            ]
            for col_name, col_type in dunning_columns:
                existing_columns = _add_column(conn, 'users', col_name, col_type, existing_columns)
            
            # ====== 最终验证：检查User模型定义的所有列是否都在数据库中 ======
            from app.models import User as UserModel
            model_columns = [c.name for c in UserModel.__table__.columns]
            missing_columns = [c for c in model_columns if c not in existing_columns]
            if missing_columns:
                logger.error(f"迁移完成后仍有缺失列: {missing_columns}，尝试逐个添加...")
                for col in missing_columns:
                    col_obj = UserModel.__table__.columns[col]
                    col_type_str = str(col_obj.type)
                    default_val = None
                    if col_obj.default is not None:
                        default_val = col_obj.default.arg
                    col_ddl = f"{col_type_str}"
                    if default_val is not None:
                        if isinstance(default_val, str):
                            col_ddl += f" DEFAULT '{default_val}'"
                        elif isinstance(default_val, bool):
                            col_ddl += f" DEFAULT {'1' if is_sqlite else 'TRUE' if default_val else '0' if is_sqlite else 'FALSE'}"
                        elif isinstance(default_val, int):
                            col_ddl += f" DEFAULT {default_val}"
                    try:
                        conn.execute(text(f"ALTER TABLE users ADD COLUMN {col} {col_ddl}"))
                        conn.commit()
                        logger.info(f"补充添加缺失列 {col} 成功")
                    except Exception as e:
                        logger.error(f"补充添加缺失列 {col} 失败: {e}")
                        conn.rollback()
            else:
                logger.info(f"数据库迁移完成，users 表共 {len(model_columns)} 列全部就绪")
            
    except Exception as e:
        logger.error(f"数据库迁移外层异常: {e}")


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
    
    def create(self, email: str, password_hash: str, username: str = None, referral_code: str = None) -> User:
        """创建新用户，自动赠送7天Pro试用并生成推荐码"""
        from datetime import timedelta
        import secrets
        import string
        
        # 设置试用期：注册后7天
        trial_end = datetime.utcnow() + timedelta(days=7)
        
        # 生成唯一的推荐码（8位字母数字）
        def generate_referral_code():
            chars = string.ascii_uppercase + string.digits
            # 排除容易混淆的字符：O, 0, I, 1, L
            chars = chars.replace('O', '').replace('0', '').replace('I', '').replace('1', '').replace('L', '')
            return ''.join(secrets.choice(chars) for _ in range(8))
        
        # 生成唯一推荐码
        my_referral_code = generate_referral_code()
        while self.db.query(User).filter(User.referral_code == my_referral_code).first():
            my_referral_code = generate_referral_code()
        
        user = User(
            email=email,
            password_hash=password_hash,
            username=username,
            trial_end_date=trial_end,  # 赠送7天Pro试用
            referral_code=my_referral_code,  # 用户的推荐码
            referred_by=referral_code  # 被谁推荐
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
    
    def get_by_referral_code(self, referral_code: str) -> User:
        """根据推荐码获取用户"""
        return self.db.query(User).filter(User.referral_code == referral_code.upper()).first()
    
    def get_referral_stats(self, user_id: int) -> dict:
        """获取用户的推荐统计"""
        user = self.get_by_id(user_id)
        if not user or not user.referral_code:
            return {"referral_code": None, "referral_count": 0}
        
        # 统计被推荐的用户数量
        count = self.db.query(User).filter(User.referred_by == user.referral_code).count()
        
        # 获取本月已发放的推荐奖励数量
        monthly_rewards = self.get_monthly_referral_rewards(user_id)
        
        return {
            "referral_code": user.referral_code,
            "referral_count": count,
            "monthly_rewards": monthly_rewards,
            "monthly_limit": 5,
            "referral_suspended": user.referral_suspended
        }
    
    def get_monthly_referral_rewards(self, user_id: int) -> int:
        """获取用户本月已发放的推荐奖励数量"""
        user = self.get_by_id(user_id)
        if not user or not user.referral_code:
            return 0
        
        # 计算本月的开始时间
        now = datetime.utcnow()
        month_start = datetime(now.year, now.month, 1)
        
        # 统计本月内，该用户推荐码注册的用户中，已获得奖励的数量
        count = self.db.query(User).filter(
            User.referred_by == user.referral_code,
            User.referral_rewarded_at >= month_start
        ).count()
        
        return count
    
    def count_referral_usage(self, referral_code: str, days: int = 7) -> int:
        """统计某推荐码在最近N天的使用次数"""
        from datetime import timedelta
        start_date = datetime.utcnow() - timedelta(days=days)
        return self.db.query(User).filter(
            User.referred_by == referral_code,
            User.created_at >= start_date
        ).count()
    
    def get_total_referral_usage(self, referral_code: str) -> int:
        """统计某推荐码的总使用次数"""
        return self.db.query(User).filter(User.referred_by == referral_code).count()
    
    def suspend_referral_code(self, user_id: int, suspended: bool = True):
        """暂停或恢复用户的推荐码"""
        user = self.get_by_id(user_id)
        if user:
            user.referral_suspended = suspended
            self.db.commit()
    
    def mark_referral_reward_pending(self, user_id: int):
        """标记用户为推荐奖励待发放状态"""
        user = self.get_by_id(user_id)
        if user:
            user.referral_reward_pending = True
            self.db.commit()
    
    def grant_referral_reward(self, user_id: int, days: int = 7) -> bool:
        """
        发放推荐奖励（延长用户Pro权限）
        返回: 是否成功发放
        """
        from datetime import timedelta
        
        user = self.get_by_id(user_id)
        if not user:
            return False
        
        now = datetime.utcnow()
        
        # 计算新的到期时间
        current_end = user.subscription_end_date or user.trial_end_date
        
        if current_end and current_end > now:
            # 在现有到期时间基础上延长
            new_end = current_end + timedelta(days=days)
        else:
            # 从现在开始计算
            new_end = now + timedelta(days=days)
        
        # 更新到期时间
        if not user.is_subscribed:
            user.trial_end_date = new_end
        else:
            user.subscription_end_date = new_end
        
        # 标记奖励已发放
        user.referral_rewarded_at = now
        
        self.db.commit()
        return True


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

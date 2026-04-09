"""
数据库迁移脚本 - 添加 Stripe 订阅字段

使用方法:
    python scripts/migrate_add_subscription_fields.py
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import inspect, text
from app.database import engine, SessionLocal

def migrate_add_subscription_fields():
    """添加 Stripe 订阅相关字段"""
    
    inspector = inspect(engine)
    
    # 获取 users 表的现有列
    existing_columns = [col['name'] for col in inspector.get_columns('users')]
    
    # 需要添加的新列
    new_columns = {
        'stripe_customer_id': 'VARCHAR(255)',
        'subscription_id': 'VARCHAR(255)',
        'subscription_status': 'VARCHAR(50) DEFAULT "none"',
        'subscription_end_date': 'DATETIME'
    }
    
    with engine.connect() as conn:
        for column_name, column_type in new_columns.items():
            if column_name not in existing_columns:
                try:
                    if 'sqlite' in str(engine.url):
                        # SQLite 语法
                        sql = f'ALTER TABLE users ADD COLUMN {column_name} {column_type}'
                    else:
                        # PostgreSQL 语法
                        sql = f'ALTER TABLE users ADD COLUMN {column_name} {column_type}'
                    
                    conn.execute(text(sql))
                    conn.commit()
                    print(f"✓ 添加字段成功: {column_name}")
                except Exception as e:
                    print(f"✗ 添加字段失败: {column_name} - {e}")
            else:
                print(f"- 字段已存在: {column_name}")
    
    print("\n数据库迁移完成!")

def rollback_subscription_fields():
    """回滚：删除订阅字段（谨慎使用）"""
    
    inspector = inspect(engine)
    existing_columns = [col['name'] for col in inspector.get_columns('users')]
    
    columns_to_remove = [
        'stripe_customer_id',
        'subscription_id', 
        'subscription_status',
        'subscription_end_date'
    ]
    
    with engine.connect() as conn:
        for column_name in columns_to_remove:
            if column_name in existing_columns:
                try:
                    if 'sqlite' in str(engine.url):
                        # SQLite 不支持 DROP COLUMN (旧版本)，需要重建表
                        print(f"SQLite 不支持直接删除列，请手动处理")
                        return
                    else:
                        sql = f'ALTER TABLE users DROP COLUMN {column_name}'
                        conn.execute(text(sql))
                        conn.commit()
                        print(f"✓ 删除字段成功: {column_name}")
                except Exception as e:
                    print(f"✗ 删除字段失败: {column_name} - {e}")
            else:
                print(f"- 字段不存在: {column_name}")
    
    print("\n字段删除完成!")

if __name__ == "__main__":
    print("=" * 50)
    print("IMVU Analytics - 数据库迁移脚本")
    print("=" * 50)
    print("\n1. 添加订阅字段")
    print("2. 回滚订阅字段")
    print("q. 退出")
    
    choice = input("\n请选择操作: ").strip()
    
    if choice == '1':
        migrate_add_subscription_fields()
    elif choice == '2':
        confirm = input("警告：此操作将删除订阅相关数据！确认执行？(y/n): ").strip().lower()
        if confirm == 'y':
            rollback_subscription_fields()
        else:
            print("已取消")
    elif choice.lower() == 'q':
        print("已退出")
    else:
        print("无效选择")

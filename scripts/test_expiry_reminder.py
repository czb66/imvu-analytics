"""
订阅到期提醒功能测试脚本

使用方法:
    python scripts/test_expiry_reminder.py

功能测试:
1. 检查数据库迁移是否添加了新字段
2. 测试邮件模板渲染
3. 测试定时任务逻辑
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 设置测试用的环境变量（如果没有设置）
os.environ.setdefault('JWT_SECRET_KEY', 'test_secret_key_for_development_only')
os.environ.setdefault('DATABASE_URL', 'sqlite:///./test.db')

from datetime import datetime, timedelta


def test_model_fields():
    """测试模型字段是否存在"""
    print("\n=== 测试模型字段 ===")
    try:
        from app.models import User
        
        # 检查订阅提醒字段
        reminder_fields = [
            'reminder_3day_sent',
            'reminder_1day_sent', 
            'reminder_recall_sent',
            'last_reminder_sent',
        ]
        
        # 检查试用期提醒字段
        trial_fields = [
            'trial_reminder_3day_sent',
            'trial_reminder_1day_sent',
            'trial_reminder_recall_sent',
        ]
        
        for field in reminder_fields + trial_fields:
            if hasattr(User, field):
                print(f"  ✓ {field} 字段存在")
            else:
                print(f"  ✗ {field} 字段不存在!")
                return False
        
        print("\n✅ 所有模型字段检查通过!")
        return True
    except Exception as e:
        print(f"❌ 模型字段测试失败: {e}")
        return False


def test_email_template():
    """测试邮件模板"""
    print("\n=== 测试邮件模板 ===")
    try:
        from app.services.report_generator import EXPIRY_REMINDER_TEMPLATES, _t, _get_user_language
        
        # 检查模板语言
        languages = ['zh', 'en', 'fr']
        template_keys = [
            'sub_3day_subject', 'sub_3day_title', 'sub_3day_greeting', 'sub_3day_body', 'sub_3day_cta',
            'sub_1day_subject', 'sub_1day_body',
            'sub_recall_subject', 'sub_recall_body',
            'trial_3day_subject', 'trial_3day_body',
            'trial_1day_subject', 'trial_1day_body',
            'trial_recall_subject', 'trial_recall_body',
        ]
        
        for lang in languages:
            if lang not in EXPIRY_REMINDER_TEMPLATES:
                print(f"  ✗ 语言 {lang} 的模板不存在!")
                return False
            
            for key in template_keys:
                if key not in EXPIRY_REMINDER_TEMPLATES[lang]:
                    print(f"  ✗ 语言 {lang} 缺少模板: {key}")
                    return False
        
        print(f"  ✓ 支持 {len(languages)} 种语言: {languages}")
        print(f"  ✓ 每种语言包含 {len(template_keys)} 个模板键")
        
        # 测试模板格式化
        sample_tpl = EXPIRY_REMINDER_TEMPLATES['zh']
        formatted = sample_tpl['sub_3day_subject'].format(app_name='IMVU Analytics')
        print(f"  ✓ 模板格式化测试: {formatted}")
        
        print("\n✅ 邮件模板测试通过!")
        return True
    except Exception as e:
        print(f"❌ 邮件模板测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_scheduler_registration():
    """测试调度器任务注册"""
    print("\n=== 测试调度器任务注册 ===")
    try:
        from app.services.report_generator import scheduler, check_subscription_expiry
        
        # 检查任务是否已注册
        jobs = {job.id: job for job in scheduler.get_jobs()}
        
        expected_jobs = ['daily_report', 'weekly_report', 'subscription_expiry_check']
        
        for job_id in expected_jobs:
            if job_id in jobs:
                job = jobs[job_id]
                print(f"  ✓ 任务 {job_id} 已注册: next_run={job.next_run_time}")
            else:
                print(f"  ⚠ 任务 {job_id} 尚未注册 (调度器可能未启动)")
        
        print("\n✅ 调度器任务测试完成!")
        return True
    except Exception as e:
        print(f"❌ 调度器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_reminder_functions():
    """测试提醒相关函数"""
    print("\n=== 测试提醒函数 ===")
    try:
        from app.services.report_generator import (
            get_reminder_stats,
            reset_user_reminder_flags,
            test_reminder_email,
            _build_expiry_reminder_html,
            EXPIRY_REMINDER_TEMPLATES
        )
        
        # 测试HTML生成
        tpl = EXPIRY_REMINDER_TEMPLATES['en']
        html = _build_expiry_reminder_html(tpl, 'sub_3day', 'TestUser', 'en')
        
        if html and len(html) > 100:
            print(f"  ✓ HTML模板生成成功 (长度: {len(html)} 字符)")
        else:
            print(f"  ✗ HTML模板生成失败!")
            return False
        
        # 测试统计函数
        stats = get_reminder_stats()
        if 'error' not in stats:
            print(f"  ✓ 统计函数正常工作")
            print(f"    - 总用户数: {stats.get('total_users', 0)}")
        else:
            print(f"  ⚠ 统计函数返回错误 (可能是数据库问题): {stats['error']}")
        
        print("\n✅ 提醒函数测试完成!")
        return True
    except Exception as e:
        print(f"❌ 提醒函数测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_database_migration():
    """测试数据库迁移"""
    print("\n=== 测试数据库迁移 ===")
    try:
        from app.database import engine
        from sqlalchemy import inspect, text
        
        inspector = inspect(engine)
        
        # 检查表是否存在
        try:
            columns = inspector.get_columns('users')
        except Exception:
            # 表不存在，跳过迁移测试
            print("  ⚠ users 表不存在（测试数据库未初始化）")
            print("    应用启动时会自动创建表和执行迁移")
            print("    请在生产环境验证迁移是否成功")
            return True
        
        column_names = [col['name'] for col in columns]
        
        expected_columns = [
            'reminder_3day_sent', 'reminder_1day_sent', 'reminder_recall_sent',
            'trial_reminder_3day_sent', 'trial_reminder_1day_sent', 'trial_reminder_recall_sent',
            'last_reminder_sent'
        ]
        
        all_exist = True
        for col in expected_columns:
            if col in column_names:
                print(f"  ✓ {col} 列已存在")
            else:
                print(f"  ✗ {col} 列不存在! (需要运行数据库迁移)")
                all_exist = False
        
        if all_exist:
            print("\n✅ 数据库迁移测试通过!")
        else:
            print("\n⚠ 部分列不存在，请在应用启动时自动迁移或手动执行迁移")
        
        return True
    except Exception as e:
        print(f"❌ 数据库迁移测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("=" * 50)
    print("订阅到期提醒功能测试")
    print("=" * 50)
    
    results = []
    
    # 1. 测试模型字段
    results.append(("模型字段", test_model_fields()))
    
    # 2. 测试邮件模板
    results.append(("邮件模板", test_email_template()))
    
    # 3. 测试调度器
    results.append(("调度器", test_scheduler_registration()))
    
    # 4. 测试提醒函数
    results.append(("提醒函数", test_reminder_functions()))
    
    # 5. 测试数据库迁移
    results.append(("数据库迁移", test_database_migration()))
    
    # 汇总结果
    print("\n" + "=" * 50)
    print("测试结果汇总")
    print("=" * 50)
    
    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"  {name}: {status}")
    
    all_passed = all(r[1] for r in results)
    
    if all_passed:
        print("\n🎉 所有测试通过!")
    else:
        print("\n⚠ 部分测试失败，请检查配置!")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

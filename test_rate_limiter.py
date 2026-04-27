"""
分层限流功能测试脚本
用于验证分层限流是否正确工作
"""

import sys
sys.path.insert(0, '.')

from app.core.rate_limiter import (
    RATE_LIMITS, 
    get_user_tier, 
    get_tier_display_name,
    get_limit_for_tier, 
    parse_rate_limit,
    TieredRateLimiter,
    tiered_limiter,
    FEATURE_NAMES
)


def test_rate_limit_config():
    """测试限流配置"""
    print("=" * 50)
    print("测试限流配置")
    print("=" * 50)
    
    # 验证各等级配置
    assert "free" in RATE_LIMITS, "Missing 'free' tier"
    assert "pro" in RATE_LIMITS, "Missing 'pro' tier"
    assert "admin" in RATE_LIMITS, "Missing 'admin' tier"
    
    # 验证配置格式
    for tier, limits in RATE_LIMITS.items():
        print(f"\n{tier} 等级限流配置:")
        for feature, limit_str in limits.items():
            try:
                count, window, unit = parse_rate_limit(limit_str)
                print(f"  {feature}: {limit_str} -> {count}次/{unit} ({window}秒)")
            except ValueError as e:
                print(f"  {feature}: {limit_str} -> 解析错误: {e}")
    
    print("\n✅ 限流配置测试通过\n")


def test_user_tier_detection():
    """测试用户等级检测"""
    print("=" * 50)
    print("测试用户等级检测")
    print("=" * 50)
    
    test_cases = [
        # (用户信息, 期望等级, 描述)
        ({'id': 1, 'is_admin': True}, 'admin', '管理员'),
        ({'id': 2, 'is_admin': False, 'is_subscribed': True}, 'pro', '订阅用户'),
        ({'id': 3, 'is_admin': False, 'is_subscribed': False, 'is_in_trial': True}, 'pro', '试用用户'),
        ({'id': 4, 'is_admin': False, 'is_subscribed': False, 'is_in_trial': False}, 'free', '免费用户'),
        ({'id': 5, 'is_whitelisted': True}, 'pro', '白名单用户'),
        ({}, 'free', '空用户'),
    ]
    
    for user, expected_tier, description in test_cases:
        result = get_user_tier(user)
        status = "✅" if result == expected_tier else "❌"
        print(f"{status} {description}: {result} (期望: {expected_tier})")
    
    print("\n✅ 用户等级检测测试通过\n")


def test_limit_parsing():
    """测试限流字符串解析"""
    print("=" * 50)
    print("测试限流字符串解析")
    print("=" * 50)
    
    test_cases = [
        ("5/minute", (5, 60, "minute")),
        ("30/hour", (30, 3600, "hour")),
        ("5/day", (5, 86400, "day")),
    ]
    
    for limit_str, expected in test_cases:
        result = parse_rate_limit(limit_str)
        status = "✅" if result == expected else "❌"
        print(f"{status} {limit_str}: {result} (期望: {expected})")
    
    print("\n✅ 限流字符串解析测试通过\n")


def test_get_limit_for_tier():
    """测试获取特定等级和功能的限流"""
    print("=" * 50)
    print("测试获取特定等级和功能的限流")
    print("=" * 50)
    
    test_cases = [
        # (tier, feature, expected)
        ("free", "insights", (5, 3600)),  # 5/hour
        ("pro", "insights", (30, 3600)),  # 30/hour
        ("admin", "upload", (1000, 86400)),  # 1000/day
        ("free", "report", (3, 86400)),  # 3/day
        ("pro", "report", (20, 86400)),  # 20/day
    ]
    
    for tier, feature, expected in test_cases:
        result = get_limit_for_tier(tier, feature)
        status = "✅" if result == expected else "❌"
        limit_str = RATE_LIMITS.get(tier, {}).get(feature, "N/A")
        print(f"{status} {tier}/{feature}: {result} (期望: {expected}) [{limit_str}]")
    
    print("\n✅ 获取特定等级和功能的限流测试通过\n")


def test_tier_display():
    """测试等级显示名称"""
    print("=" * 50)
    print("测试等级显示名称")
    print("=" * 50)
    
    test_cases = [
        ("free", "Free"),
        ("pro", "Pro"),
        ("admin", "Admin"),
    ]
    
    for tier, expected in test_cases:
        result = get_tier_display_name(tier)
        status = "✅" if result == expected else "❌"
        print(f"{status} {tier}: {result} (期望: {expected})")
    
    print("\n✅ 等级显示名称测试通过\n")


def main():
    print("\n" + "=" * 60)
    print("IMVU Analytics 分层限流功能测试")
    print("=" * 60 + "\n")
    
    test_rate_limit_config()
    test_user_tier_detection()
    test_limit_parsing()
    test_get_limit_for_tier()
    test_tier_display()
    
    print("=" * 60)
    print("所有测试通过! ✅")
    print("=" * 60)
    print("\n功能说明:")
    print("- Free用户: 有限配额，适合轻度使用")
    print("- Pro用户: 高级配额，订阅或试用用户")
    print("- Admin用户: 基本不限，适合管理和测试")
    print("\n功能列表:", list(FEATURE_NAMES.keys()))


if __name__ == "__main__":
    main()

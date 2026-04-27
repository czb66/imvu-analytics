# IMVU Analytics 订阅到期提醒功能

## 功能概述

实现了一套完整的订阅到期提醒机制，帮助减少用户流失并提升续费率。

## 主要功能

### 1. 多时机提醒

| 提醒类型 | 订阅用户 | 试用期用户 |
|---------|---------|----------|
| 3天前提醒 | ✅ | ✅ |
| 1天前提醒 | ✅ | ✅ |
| 过期7天内召回 | ✅ | ✅ |

### 2. 三语支持

- 🇨🇳 中文 (zh)
- 🇺🇸 English (en)
- 🇫🇷 Français (fr)

语言自动根据用户邮箱域名判断（`.cn`/`.com.cn` → 中文，其他 → 英文）

### 3. 防重复发送机制

每个订阅周期内每种提醒只发送一次，通过以下字段控制：

```python
# 订阅用户
reminder_3day_sent = Column(Boolean, default=False)  # 3天提醒已发
reminder_1day_sent = Column(Boolean, default=False)  # 1天提醒已发
reminder_recall_sent = Column(Boolean, default=False)  # 召回邮件已发
last_reminder_sent = Column(DateTime, nullable=True)  # 最后提醒时间

# 试用期用户
trial_reminder_3day_sent = Column(Boolean, default=False)
trial_reminder_1day_sent = Column(Boolean, default=False)
trial_reminder_recall_sent = Column(Boolean, default=False)
```

**续费后自动重置**：当用户续费成功时，这些标志会自动重置。

## 文件变更

### app/models.py
- 添加 7 个新字段到 User 模型

### app/database.py
- 添加迁移：自动为现有数据库添加新字段

### app/services/report_generator.py
- 添加到期提醒邮件模板（中英法三语）
- 添加 `check_subscription_expiry()` 定时任务
- 添加 `get_reminder_stats()` 统计函数
- 添加 `test_reminder_email()` 测试函数
- 添加 `reset_user_reminder_flags()` 重置函数
- 在调度器注册新任务

### app/routers/subscription.py
- 在 `update_user_subscription()` 中添加续费后重置提醒标志的逻辑

### app/routers/admin.py
- `GET /api/admin/reminder/stats` - 获取提醒统计
- `POST /api/admin/reminder/test` - 测试发送提醒邮件
- `POST /api/admin/reminder/reset` - 重置用户提醒标志
- `POST /api/admin/reminder/trigger` - 手动触发提醒检查

## API 接口

### 获取提醒统计

```bash
GET /api/admin/reminder/stats
Authorization: Bearer <admin_token>

Response:
{
  "success": true,
  "data": {
    "total_users": 100,
    "sent": {
      "sub_3day": 5,
      "sub_1day": 3,
      "sub_recall": 10,
      "trial_3day": 8,
      "trial_1day": 2,
      "trial_recall": 15
    },
    "pending": {
      "sub_3day": 2,
      "sub_1day": 1,
      ...
    }
  }
}
```

### 测试发送提醒邮件

```bash
POST /api/admin/reminder/test?user_id=123&reminder_type=sub_3day
Authorization: Bearer <admin_token>

# reminder_type 可选值:
# - sub_3day: 订阅3天提醒
# - sub_1day: 订阅1天提醒
# - sub_recall: 订阅召回
# - trial_3day: 试用期3天提醒
# - trial_1day: 试用期1天提醒
# - trial_recall: 试用期召回
```

### 重置用户提醒标志

```bash
POST /api/admin/reminder/reset?user_id=123&is_trial=false
Authorization: Bearer <admin_token>
```

## 定时任务

### 执行时间
- **UTC 1:00** = 北京时间 9:00
- 每天执行一次

### 调度器中的任务
```
┌─────────────────────────────────────────────────────────┐
│                    APScheduler                           │
├─────────────────────────────────────────────────────────┤
│  daily_report         │ 每天 REPORT_CRON_HOUR:MM UTC  │
│  weekly_report         │ 每周一 REPORT_CRON_HOUR:MM UTC │
│  subscription_expiry   │ 每天 01:00 UTC                 │
└─────────────────────────────────────────────────────────┘
```

## 邮件模板预览

### 3天/1天提醒邮件
- 蓝色主题色 (`#667eea → #764ba2`)
- 包含到期日期强调
- CTA 按钮指向 /pricing

### 召回邮件
- 绿色主题色 (`#28a745 → #20c997`)
- 包含限时优惠信息
- 强调欢迎回来

### 紧急提醒（1天）
- 橙黄色主题色 (`#ffc107 → #fd7e14`)
- 更强的紧迫感

## 测试验证

```bash
# 运行功能测试
python scripts/test_expiry_reminder.py
```

## 注意事项

1. **白名单用户不受影响**：`is_whitelisted=True` 的用户不会收到提醒
2. **邮件发送失败不影响其他用户**：每个用户的发送都是独立的 try-catch
3. **迁移安全**：使用 `ALTER TABLE ... ADD COLUMN`，只在列不存在时执行
4. **生产环境验证**：部署后建议手动触发一次提醒检查验证功能

## 邮件内容示例

### 中文 - 3天提醒
```
主题: ⏰ IMVU Analytics - 您的订阅将在3天后到期

亲爱的 用户名，

您的 IMVU Analytics 订阅将在 **3 天后** 到期。为了不影响您继续使用我们的服务，请及时续费。

[立即续费]

---
此邮件由 IMVU Analytics 自动发送
```

### 英文 - 召回邮件
```
Subject: 🎉 IMVU Analytics - Welcome back! Special offer inside

Dear Username,

Your IMVU Analytics subscription has expired. As a valued member, 
we're offering you a **limited-time discount** to come back!

[View Offer]
```

# 修复 Admin 页面 JavaScript 错误

## 问题
- Admin 页面加载时卡住
- JavaScript 报错：`translations` 被声明了两次
  - 位置1：admin.html:335
  - 位置2：i18n.js

## 解决方案
移除 admin.html 中重复的 `translations` 声明，只保留 i18n.js 中的定义

## 需要检查的文件
- static/js/i18n.js (应该包含 translations 定义)
- templates/admin.html (需要移除重复的 translations)
- templates/auth.js (检查是否也需要修正)

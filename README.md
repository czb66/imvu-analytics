# Azen 营销数据分析平台

基于 Python + FastAPI 的营销数据分析工具，支持 XML 数据上传、多维度分析和自动化报告。

## 功能特性

### 📊 仪表盘模块
- 核心指标卡片：总销售额、总利润、总订单、平均转化率
- Top 10 产品可视化（按利润/销售额）
- 可见性分布对比（可见 vs 隐藏产品）
- 流量分析（自然流量 vs 付费流量）
- 产品筛选和搜索功能

### 🔍 深度诊断模块
- **销售诊断**：价格区间分析、转化漏斗、高利润产品识别
- **流量诊断**：自然流量 vs 付费流量效果对比、ROI分析
- **用户行为诊断**：加购→收藏→下单转化率分析
- **异常检测**：基于统计的销量异常波动检测

### 🤖 AI 智能洞察模块 (新功能!)
- **仪表盘洞察**：总体销售趋势解读、Top产品表现分析、核心指标异常提醒
- **诊断洞察**：销量下滑/增长原因识别、曝光-转化漏斗分析、异常产品自动解读
- **对比洞察**：多数据集对比结论、排名变化分析、趋势对比总结
- 支持 DeepSeek API（低成本、中文友好）
- 离线模式：未配置 API 时提供基于规则的基础洞察

### 📄 报告模块
- 一键生成完整HTML报告
- 支持定时自动生成（每天UTC 1:00）
- 邮件发送报告功能
- 报告历史管理

## 技术栈

- **后端**：Python 3.10+ / FastAPI
- **数据处理**：Pandas / NumPy
- **数据库**：SQLite
- **定时任务**：APScheduler
- **前端**：Bootstrap 5 / Vue.js / Chart.js
- **邮件**：smtplib

## 快速开始

### 方式一：本地运行

```bash
# 1. 克隆/下载项目
cd marketing_analytics

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量（可选）
cp .env.example .env
# 编辑 .env 文件填入SMTP配置

# 5. 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 方式二：Docker部署

```bash
# 构建镜像
docker build -t marketing-analytics .

# 运行容器
docker run -d \
  --name marketing-analytics \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -e SMTP_HOST=smtp.gmail.com \
  -e SMTP_PORT=587 \
  -e SMTP_USER=your@email.com \
  -e SMTP_PASSWORD=yourpassword \
  -e EMAIL_TO=dest@email.com \
  marketing-analytics
```

### 方式三：Docker Compose

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

## 访问地址

- **Web界面**：http://localhost:8000
- **API文档**：http://localhost:8000/docs
- **备用API文档**：http://localhost:8000/redoc

## 使用说明

### 1. 上传数据

访问仪表盘页面，点击上传区域或拖拽XML文件：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<product_list>
    <product_list_entry 
        product_id="68521162" 
        product_name="示例产品" 
        price="715" 
        profit="300" 
        visible="Y" 
        direct_sales="1500" 
        indirect_sales="800" 
        promoted_sales="1200" 
        cart_adds="250" 
        wishlist_adds="180" 
        organic_impressions="50000" 
        paid_impressions="30000" />
</product_list>
```

### 2. 查看仪表盘

上传数据后自动展示：
- 核心指标卡片
- Top产品图表
- 可见性分布
- 流量对比

### 3. 深度诊断

访问诊断页面获取：
- 转化漏斗分析
- 价格区间分析
- ROI分析
- 异常检测和预警

### 4. 生成报告

在报告中心：
- 点击"生成完整报告"快速生成
- 配置自定义报告选项
- 启用邮件发送自动推送

## 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `DEBUG` | 调试模式 | `False` |
| `HOST` | 服务地址 | `0.0.0.0` |
| `PORT` | 服务端口 | `8000` |
| `DATABASE_URL` | 数据库连接 | `sqlite:///./marketing_analytics.db` |
| `SMTP_HOST` | SMTP服务器 | - |
| `SMTP_PORT` | SMTP端口 | `587` |
| `SMTP_USER` | 发件邮箱 | - |
| `SMTP_PASSWORD` | 邮箱密码 | - |
| `EMAIL_TO` | 默认收件人 | - |
| `REPORT_CRON_HOUR` | 报告生成小时(UTC) | `1` |
| `DEEPSEEK_API_KEY` | DeepSeek API密钥 | - |

### .env 文件示例

```env
# 应用配置
DEBUG=False
HOST=0.0.0.0
PORT=8000

# DeepSeek API 配置 (AI洞察功能)
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# 邮件配置
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_TO=team@company.com

# 报告配置
REPORT_CRON_HOUR=1
REPORT_CRON_MINUTE=0
```

## API 接口

### 上传模块
- `POST /api/upload/` - 上传XML文件
- `POST /api/upload/validate` - 验证XML结构
- `GET /api/upload/template` - 下载XML模板

### 仪表盘
- `GET /api/dashboard/summary` - 获取汇总指标
- `GET /api/dashboard/top-products` - Top产品列表
- `GET /api/dashboard/visibility` - 可见性分析
- `GET /api/dashboard/traffic` - 流量分析
- `GET /api/dashboard/products` - 产品列表（支持筛选）

### 诊断模块
- `GET /api/diagnosis/full-report` - 完整诊断报告
- `GET /api/diagnosis/conversion-funnel` - 转化漏斗
- `GET /api/diagnosis/price-range` - 价格区间分析
- `GET /api/diagnosis/high-profit` - 高利润产品
- `GET /api/diagnosis/roi` - ROI分析
- `GET /api/diagnosis/anomalies` - 异常检测
- `GET /api/diagnosis/low-conversion-alerts` - 低转化预警

### AI 洞察模块
- `POST /api/insights/dashboard` - 生成仪表盘洞察
- `POST /api/insights/diagnosis` - 生成诊断洞察
- `POST /api/insights/compare` - 生成对比洞察
- `GET /api/insights/config-status` - 检查API配置状态

### 报告模块
- `GET /api/report/generate` - 生成HTML报告
- `POST /api/report/generate` - 创建自定义报告
- `GET /api/report/download/{filename}` - 下载报告
- `GET /api/report/history` - 报告历史

## 项目结构

```
marketing_analytics/
├── app/
│   ├── main.py              # FastAPI 主入口
│   ├── models.py            # 数据模型
│   ├── database.py          # 数据库操作
│   ├── routers/             # API路由
│   │   ├── upload.py       # 文件上传
│   │   ├── dashboard.py    # 仪表盘
│   │   ├── diagnosis.py    # 深度诊断
│   │   ├── compare.py      # 数据对比
│   │   ├── insights.py     # AI洞察
│   │   └── report.py       # 报告生成
│   ├── services/           # 业务服务
│   │   ├── parser.py       # XML解析
│   │   ├── analytics.py    # 数据分析
│   │   ├── insights.py     # AI洞察服务
│   │   └── email_service.py # 邮件服务
│   └── templates/          # HTML模板
│       ├── dashboard.html  # 仪表盘页面
│       ├── diagnosis.html  # 诊断页面
│       ├── compare.html    # 对比页面
│       ├── settings.html   # 设置页面
│       └── ...
├── static/                  # 静态资源
│   ├── i18n.js             # 多语言配置
│   └── ...
├── config.py               # 配置文件
├── requirements.txt        # 依赖清单
├── Dockerfile              # Docker配置
├── docker-compose.yml     # Docker编排
└── README.md              # 项目文档
```

## 数据字段说明

| XML属性 | 说明 | 数据类型 |
|---------|------|----------|
| product_id | 产品ID | string |
| product_name | 产品名称 | string |
| price | 批发价格 | float |
| profit | 利润 | float |
| visible | 是否可见 (Y/N) | string |
| direct_sales | 直接销售额 | float |
| indirect_sales | 间接销售额 | float |
| promoted_sales | 推广期销售额 | float |
| cart_adds | 加购数 | int |
| wishlist_adds | 收藏数 | int |
| organic_impressions | 自然展示 | int |
| paid_impressions | 付费展示 | int |

## AI 洞察功能配置

### 配置方式

AI 洞察功能支持两种配置方式：

#### 方式一：服务端环境变量（推荐用于部署环境）

在环境变量或 `.env` 文件中配置：

```env
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

#### 方式二：浏览器本地存储（无需重新部署）

1. 访问应用后点击侧边栏的「设置」按钮
2. 输入您的 DeepSeek API Key
3. 点击「保存 API Key」

API Key 将保存在浏览器本地存储中，刷新页面不会丢失。

### 获取 DeepSeek API Key

1. 访问 [DeepSeek Platform](https://platform.deepseek.com/api_keys)
2. 注册/登录账户
3. 进入「API Keys」页面
4. 创建新的 API Key 并复制

### 功能说明

| 页面 | 洞察内容 |
|------|---------|
| 仪表盘 | 总体销售趋势、Top产品表现、异常提醒 |
| 深度诊断 | 销量诊断原因、漏斗问题分析、异常解读 |
| 数据对比 | 多数据集对比结论、排名变化、趋势总结 |

### 离线模式

未配置 API Key 时，系统会提供基于规则的基础洞察，包含：
- 销售趋势的基本判断
- 产品可见性提醒
- 转化率的简单分析

## 注意事项

1. **数据安全**：敏感配置使用环境变量，避免硬编码
2. **文件大小**：默认最大上传50MB，可在config.py中调整
3. **邮件发送**：Gmail需要开启"应用专用密码"
4. **定时任务**：默认UTC时间，部署时注意时区转换

## 许可证

MIT License

## 联系方式

如有问题，请提交 Issue。

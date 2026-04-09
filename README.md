# IMVU Analytics Platform

基于 Python + FastAPI 的营销数据分析平台，支持 XML 数据上传、多维度分析、自动化报告和用户认证。

## 功能特性

### 🔐 用户认证
- 邮箱注册和登录
- JWT Token 认证（7天有效期）
- "记住我"功能（30天有效期）
- 密码加密存储（bcrypt）
- 用户数据隔离

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

### 🤖 AI 智能洞察模块
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
- **数据库**：SQLite / PostgreSQL
- **认证**：JWT / bcrypt
- **定时任务**：APScheduler
- **前端**：Bootstrap 5 / Chart.js
- **邮件**：aiosmtplib

## 快速开始

### 方式一：本地运行

```bash
# 1. 克隆项目
git clone https://github.com/czb66/imvu-analytics.git
cd imvu-analytics

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 文件填入配置

# 5. 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 方式二：Docker部署

```bash
# 构建镜像
docker build -t imvu-analytics .

# 运行容器
docker run -d \
  --name imvu-analytics \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -e JWT_SECRET_KEY=your-secret-key \
  -e SMTP_HOST=smtp.gmail.com \
  -e SMTP_PORT=587 \
  -e SMTP_USER=your@email.com \
  -e SMTP_PASSWORD=yourpassword \
  imvu-analytics
```

### 方式三：Railway 部署

1. Fork 此仓库
2. 在 [Railway](https://railway.app) 创建新项目
3. 连接 GitHub 仓库
4. 添加环境变量：
   - `JWT_SECRET_KEY`（自动生成）
   - `DATABASE_URL`（使用 Railway PostgreSQL）
5. 部署

## 访问地址

- **登录页**：http://localhost:8000/login
- **注册页**：http://localhost:8000/register
- **仪表盘**：http://localhost:8000/dashboard
- **API文档**：http://localhost:8000/docs

## 使用说明

### 1. 注册账号

访问 `/register` 页面注册新账号：
- 邮箱：作为登录凭证
- 密码：至少8位
- 用户名：（可选）

### 2. 登录

访问 `/login` 页面登录：
- 可以勾选"记住我"延长登录有效期
- Token 保存在浏览器 localStorage

### 3. 上传数据

登录后访问仪表盘页面，点击上传区域或拖拽XML文件：

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

### 4. 查看分析

- **仪表盘**：核心指标和可视化图表
- **深度诊断**：转化漏斗、价格区间、ROI分析
- **数据对比**：多数据集对比分析
- **AI洞察**：智能分析和建议

### 5. 生成报告

在报告中心生成和下载分析报告。

## 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `DEBUG` | 调试模式 | `False` |
| `HOST` | 服务地址 | `0.0.0.0` |
| `PORT` | 服务端口 | `8000` |
| `DATABASE_URL` | 数据库连接 | SQLite本地文件 |
| `JWT_SECRET_KEY` | JWT密钥 | **必填** |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Token有效期(分钟) | `10080` (7天) |
| `JWT_REMEMBER_EXPIRE_MINUTES` | 记住我有效期 | `43200` (30天) |
| `SMTP_HOST` | SMTP服务器 | - |
| `SMTP_PORT` | SMTP端口 | `587` |
| `SMTP_USER` | 发件邮箱 | - |
| `SMTP_PASSWORD` | 邮箱密码 | - |
| `DEEPSEEK_API_KEY` | DeepSeek API密钥 | - |

### .env 文件示例

```env
# JWT 认证配置（必填）
JWT_SECRET_KEY=your-super-secret-key-change-in-production

# 数据库配置
DATABASE_URL=sqlite:///./data/marketing_analytics.db
# 或使用 PostgreSQL：
# DATABASE_URL=postgresql://user:password@host:5432/dbname

# DeepSeek API 配置 (AI洞察功能)
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# 邮件配置
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your@gmail.com
SMTP_PASSWORD=your-app-password
```

## API 接口

### 认证模块
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/logout` - 登出
- `GET /api/auth/me` - 获取当前用户信息
- `POST /api/auth/check-email` - 检查邮箱是否已注册

### 上传模块
- `POST /api/upload/` - 上传XML文件（需登录）
- `POST /api/upload/validate` - 验证XML结构
- `GET /api/upload/template` - 下载XML模板

### 仪表盘
- `GET /api/dashboard/summary` - 获取汇总指标
- `GET /api/dashboard/top-products` - Top产品列表
- `GET /api/dashboard/visibility` - 可见性分析
- `GET /api/dashboard/traffic` - 流量分析
- `GET /api/dashboard/products` - 产品列表

### 诊断模块
- `GET /api/diagnosis/full-report` - 完整诊断报告
- `GET /api/diagnosis/conversion-funnel` - 转化漏斗
- `GET /api/diagnosis/price-range` - 价格区间分析
- `GET /api/diagnosis/high-profit` - 高利润产品
- `GET /api/diagnosis/roi` - ROI分析
- `GET /api/diagnosis/anomalies` - 异常检测

### AI 洞察模块
- `POST /api/insights/dashboard` - 生成仪表盘洞察
- `POST /api/insights/diagnosis` - 生成诊断洞察
- `POST /api/insights/compare` - 生成对比洞察

### 报告模块
- `GET /api/report/generate` - 生成HTML报告
- `POST /api/report/generate` - 创建自定义报告
- `GET /api/report/download/{filename}` - 下载报告
- `GET /api/report/history` - 报告历史

## 数据隔离

系统实现完整的用户数据隔离：
- 每个用户只能看到自己的数据集
- 上传的数据自动关联当前用户
- API 查询自动过滤用户数据
- 数据集 ID 验证确保用户只能访问自己的数据

## 项目结构

```
imvu-analytics/
├── app/
│   ├── main.py              # FastAPI 主入口
│   ├── models.py            # 数据模型（含User模型）
│   ├── database.py          # 数据库操作（含用户仓储）
│   ├── routers/             # API路由
│   │   ├── auth.py         # 认证路由
│   │   ├── upload.py       # 文件上传
│   │   ├── dashboard.py    # 仪表盘
│   │   ├── diagnosis.py    # 深度诊断
│   │   ├── compare.py      # 数据对比
│   │   ├── insights.py     # AI洞察
│   │   └── report.py       # 报告生成
│   ├── services/           # 业务服务
│   │   ├── auth.py         # 认证服务
│   │   ├── parser.py       # XML解析
│   │   ├── analytics.py    # 数据分析
│   │   ├── insights.py     # AI洞察服务
│   │   └── email_service.py # 邮件服务
│   └── templates/          # HTML模板
│       ├── login.html      # 登录页面
│       ├── register.html   # 注册页面
│       ├── dashboard.html  # 仪表盘页面
│       └── ...
├── static/                  # 静态资源
│   ├── auth.js             # 前端认证模块
│   ├── i18n.js             # 多语言配置
│   └── ...
├── config.py               # 配置文件
├── requirements.txt        # 依赖清单
├── Dockerfile              # Docker配置
├── railway.json            # Railway配置
└── README.md               # 项目文档
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

### 获取 DeepSeek API Key

1. 访问 [DeepSeek Platform](https://platform.deepseek.com/api_keys)
2. 注册/登录账户
3. 进入「API Keys」页面
4. 创建新的 API Key 并复制

### 配置方式

#### 方式一：环境变量（推荐用于部署环境）

```env
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

#### 方式二：设置页面（无需重新部署）

1. 登录后点击侧边栏的「设置」
2. 输入 DeepSeek API Key
3. 点击「保存 API Key」

## 注意事项

1. **JWT密钥**：生产环境必须设置复杂的随机密钥
2. **数据安全**：敏感配置使用环境变量
3. **文件大小**：默认最大上传50MB
4. **邮件发送**：Gmail需要开启"应用专用密码"
5. **定时任务**：默认UTC时间

## 许可证

MIT License

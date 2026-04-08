# 构建阶段
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建数据目录
RUN mkdir -p ./data ./reports

# 暴露端口（Railway会自动分配）
EXPOSE $PORT

# 环境变量
ENV PYTHONUNBUFFERED=1
ENV HOST=0.0.0.0

# 启动命令（Railway会覆盖PORT环境变量）
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}

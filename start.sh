#!/bin/bash
# 启动脚本 - 营销数据分析平台

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Azen 营销数据分析平台 启动脚本${NC}"
echo -e "${GREEN}========================================${NC}"

# 检查Python版本
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
if [[ $(echo "$PYTHON_VERSION < 3.8" | bc -l) -eq 1 ]]; then
    echo -e "${RED}错误: 需要 Python 3.8 或更高版本${NC}"
    echo -e "${YELLOW}当前版本: $PYTHON_VERSION${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} Python 版本: $PYTHON_VERSION"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}创建虚拟环境...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✓${NC} 虚拟环境已创建"
fi

# 激活虚拟环境
echo -e "${YELLOW}激活虚拟环境...${NC}"
source venv/bin/activate

# 安装依赖
if [ -f "requirements.txt" ]; then
    echo -e "${YELLOW}安装依赖...${NC}"
    pip install -q -r requirements.txt
    echo -e "${GREEN}✓${NC} 依赖安装完成"
fi

# 检查.env文件
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo -e "${YELLOW}复制环境变量文件...${NC}"
        cp .env.example .env
        echo -e "${GREEN}✓${NC} .env 文件已创建，请编辑配置"
    fi
fi

# 创建必要目录
mkdir -p data reports
echo -e "${GREEN}✓${NC} 数据目录已创建"

# 启动服务
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  启动服务中...${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "访问地址: ${YELLOW}http://localhost:8000${NC}"
echo -e "API文档:  ${YELLOW}http://localhost:8000/docs${NC}"
echo ""
echo -e "按 ${RED}Ctrl+C${NC} 停止服务"
echo ""

# 启动uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

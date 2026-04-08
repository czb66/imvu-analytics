@echo off
REM 启动脚本 - Windows - 营销数据分析平台

echo ========================================
echo   Azen 营销数据分析平台 启动脚本
echo ========================================
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)
echo [OK] Python检查通过

REM 创建虚拟环境
if not exist "venv" (
    echo 创建虚拟环境...
    python -m venv venv
    echo [OK] 虚拟环境已创建
)

REM 激活虚拟环境并安装依赖
echo 激活虚拟环境...
call venv\Scripts\activate.bat

if exist "requirements.txt" (
    echo 安装依赖...
    pip install -r requirements.txt
    echo [OK] 依赖安装完成
)

REM 创建目录
if not exist "data" mkdir data
if not exist "reports" mkdir reports
echo [OK] 数据目录已创建

REM 复制.env
if not exist ".env" (
    if exist ".env.example" (
        copy .env.example .env
        echo [OK] .env 文件已创建，请编辑配置
    )
)

echo.
echo ========================================
echo   启动服务中...
echo ========================================
echo.
echo 访问地址: http://localhost:8000
echo API文档:  http://localhost:8000/docs
echo.
echo 按 Ctrl+C 停止服务
echo.

REM 启动uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

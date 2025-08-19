#!/bin/bash

# 本地测试环境启动脚本
# 用于快速启动本地测试环境的web服务

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 启动本地测试环境${NC}"
echo "======================================"

# 获取项目根目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"  # 向上两级到项目根目录

echo "项目根目录: $PROJECT_ROOT"

# 检查是否已配置测试环境
if [ ! -f "$PROJECT_ROOT/backend/web/.env" ]; then
    echo -e "${RED}❌ 未找到测试环境配置文件${NC}"
    echo "请先运行: ./deploy-test.sh"
    exit 1
fi

# 检查.env文件中的环境配置
if ! grep -q "ENVIRONMENT=test" "$PROJECT_ROOT/backend/web/.env"; then
    echo -e "${YELLOW}⚠️  当前不是测试环境配置${NC}"
    echo "请先运行: ./deploy-test.sh 或 ./switch-env.sh test"
    exit 1
fi

echo -e "${GREEN}✅ 测试环境配置检查通过${NC}"

# 进入web目录
cd "$PROJECT_ROOT/backend/web"

# 检查Python依赖
echo "\n📦 检查Python依赖..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt > /dev/null 2>&1 || {
        echo -e "${YELLOW}⚠️  依赖安装可能有问题，继续启动...${NC}"
    }
fi

# 显示当前环境信息
echo "\n📊 当前环境信息:"
echo "   环境: test"
echo "   股票表: stock_test"
echo "   基金表: fund_test"
echo "   启动端口: 8000"

echo "\n🔥 启动Web服务..."
echo -e "${GREEN}服务将在 http://localhost:8000 启动${NC}"
echo -e "${GREEN}健康检查: http://localhost:8000/health${NC}"
echo "\n按 Ctrl+C 停止服务"
echo "======================================"

# 加载环境变量
set -a  # 自动导出所有变量
source .env
set +a  # 关闭自动导出

# 启动服务
python main.py
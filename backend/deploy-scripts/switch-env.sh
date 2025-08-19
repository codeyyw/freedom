#!/bin/bash

# 环境切换脚本
# 使用方法: ./switch-env.sh [test|prod|dev]

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 显示使用帮助
show_help() {
    echo "环境切换脚本"
    echo ""
    echo "使用方法:"
    echo "  $0 [环境名称]"
    echo ""
    echo "支持的环境:"
    echo "  test        - 测试环境 (使用 stock_test, fund_test 表)"
    echo "  prod        - 生产环境 (使用 stock_info, fund_info 表)"
    echo "  dev         - 开发环境 (使用 stock_info_dev, fund_info_dev 表)"
    echo ""
    echo "示例:"
    echo "  $0 test     # 切换到测试环境"
    echo "  $0 prod     # 切换到生产环境"
    echo "  $0 dev      # 切换到开发环境"
    echo ""
}

# 检查参数
if [ $# -eq 0 ] || [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    show_help
    exit 0
fi

ENV_NAME="$1"

# 验证环境名称
case $ENV_NAME in
    "test")
        ENVIRONMENT="test"
        STOCK_TABLE="stock_test"
        FUND_TABLE="fund_test"
        ;;
    "prod"|"production")
        ENVIRONMENT="production"
        STOCK_TABLE="stock_info"
        FUND_TABLE="fund_info"
        ;;
    "dev"|"development")
        ENVIRONMENT="development"
        STOCK_TABLE="stock_info_dev"
        FUND_TABLE="fund_info_dev"
        ;;
    *)
        echo -e "${RED}❌ 错误: 不支持的环境名称 '$ENV_NAME'${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}环境切换工具${NC}"
echo -e "${BLUE}========================================${NC}"

# 显示当前环境信息
echo -e "${YELLOW}目标环境信息:${NC}"
echo "  环境名称: $ENVIRONMENT"
echo "  股票表: $STOCK_TABLE"
echo "  基金表: $FUND_TABLE"
echo ""

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/../.." && pwd )"

# 检查 .env 文件
WEB_ENV_FILE="$PROJECT_ROOT/backend/web/.env"
TASK_ENV_FILE="$PROJECT_ROOT/backend/task/.env"

echo -e "${YELLOW}📝 更新环境配置文件...${NC}"

# 更新 web 目录的 .env 文件
if [ -f "$WEB_ENV_FILE" ]; then
    # 备份原文件
    cp "$WEB_ENV_FILE" "$WEB_ENV_FILE.backup.$(date +%Y%m%d_%H%M%S)"
    
    # 更新 ENVIRONMENT 变量
    if grep -q "^ENVIRONMENT=" "$WEB_ENV_FILE"; then
        sed -i.tmp "s/^ENVIRONMENT=.*/ENVIRONMENT=$ENVIRONMENT/" "$WEB_ENV_FILE"
        rm "$WEB_ENV_FILE.tmp"
    else
        echo "ENVIRONMENT=$ENVIRONMENT" >> "$WEB_ENV_FILE"
    fi
    echo "  ✓ 更新 web/.env"
else
    # 创建新的 .env 文件
    cat > "$WEB_ENV_FILE" << EOF
# 环境配置
ENVIRONMENT=$ENVIRONMENT

# 数据库配置
PG_HOST=localhost
PG_PORT=5432
PG_USER=postgres
PG_PASSWORD=your-password
PG_DB=your-database
PG_HOST_OUT=localhost

# 应用配置
DEFAULT_LIMIT=500
MAX_LIMIT=1000
CACHE_TTL=300
LOG_LEVEL=INFO
EOF
    echo "  ✓ 创建 web/.env"
fi

# 更新 task 目录的 .env 文件
if [ -f "$TASK_ENV_FILE" ]; then
    # 备份原文件
    cp "$TASK_ENV_FILE" "$TASK_ENV_FILE.backup.$(date +%Y%m%d_%H%M%S)"
    
    # 更新 ENVIRONMENT 变量
    if grep -q "^ENVIRONMENT=" "$TASK_ENV_FILE"; then
        sed -i.tmp "s/^ENVIRONMENT=.*/ENVIRONMENT=$ENVIRONMENT/" "$TASK_ENV_FILE"
        rm "$TASK_ENV_FILE.tmp"
    else
        echo "ENVIRONMENT=$ENVIRONMENT" >> "$TASK_ENV_FILE"
    fi
    echo "  ✓ 更新 task/.env"
else
    # 创建新的 .env 文件
    cat > "$TASK_ENV_FILE" << EOF
# 环境配置
ENVIRONMENT=$ENVIRONMENT

# 数据库配置
PG_HOST=localhost
PG_PORT=5432
PG_USER=postgres
PG_PASSWORD=your-password
PG_DB=your-database
EOF
    echo "  ✓ 创建 task/.env"
fi

# 设置当前 shell 环境变量
echo -e "\n${YELLOW}🔧 设置当前 shell 环境变量...${NC}"
export ENVIRONMENT="$ENVIRONMENT"
echo "  ✓ export ENVIRONMENT=$ENVIRONMENT"

# 验证配置
echo -e "\n${YELLOW}🔍 验证配置...${NC}"

# 检查 Python 配置加载
cd "$PROJECT_ROOT/backend/web"
if command -v python3 &> /dev/null; then
    python3 -c "
import os
os.environ['ENVIRONMENT'] = '$ENVIRONMENT'
from config import config
print(f'  ✓ 环境: {config.ENVIRONMENT}')
print(f'  ✓ 股票表: {config.STOCK_TABLE}')
print(f'  ✓ 基金表: {config.FUND_TABLE}')
" 2>/dev/null || echo "  ⚠️  Python 配置验证失败，请检查依赖"
else
    echo "  ⚠️  Python3 未安装，跳过配置验证"
fi

# 显示后续步骤
echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}✅ 环境切换完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "${YELLOW}当前环境配置:${NC}"
echo "  环境: $ENVIRONMENT"
echo "  股票表: $STOCK_TABLE"
echo "  基金表: $FUND_TABLE"
echo ""
echo -e "${YELLOW}后续步骤:${NC}"
echo "1. 确保数据库中存在对应的表"
if [ "$ENVIRONMENT" = "test" ]; then
    echo "   - 执行: psql -f stock_test_table.sql"
    echo "   - 执行: psql -f fund_test_table.sql"
elif [ "$ENVIRONMENT" = "development" ]; then
    echo "   - 创建开发环境表 (stock_info_dev, fund_info_dev)"
fi
echo "2. 重启应用服务以加载新配置"
echo "3. 验证 API 健康检查接口"
echo ""
echo -e "${YELLOW}验证命令:${NC}"
echo "  # 本地测试"
echo "  cd backend/web && python main.py"
echo ""
echo "  # 健康检查"
echo "  curl http://localhost:5000/"
echo ""
echo -e "${BLUE}========================================${NC}"
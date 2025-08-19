#!/bin/bash

# 测试环境部署脚本
# 使用方法: ./deploy-test.sh

set -e  # 遇到错误立即退出

echo "========================================"
echo "开始部署到测试环境"
echo "========================================"

# 设置环境变量
export ENVIRONMENT=test
echo "✓ 环境设置: $ENVIRONMENT"

# 设置默认数据库配置（如果环境变量未设置）
echo "🔍 检查和设置数据库配置..."

# 设置默认值
export PG_DB="${PG_DB:-tushare}"
export PG_HOST="${PG_HOST:-rm-cn-yjp4duh2d00013.rwlb.rds.aliyuncs.com}"
export PG_PASSWORD="${PG_PASSWORD:-Yyw970512}"
export PG_PORT="${PG_PORT:-5432}"
export PG_USER="${PG_USER:-yuanyiwei}"

echo "✅ 数据库配置:"
echo "   主机: $PG_HOST"
echo "   用户: $PG_USER"
echo "   数据库: $PG_DB"
echo "   端口: $PG_PORT"

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/../.." && pwd )"

echo "项目根目录: $PROJECT_ROOT"

# 本地测试环境配置
echo "\n🔧 配置本地测试环境..."

# 创建web服务的.env文件
echo "📝 配置web服务环境变量..."
cd "$PROJECT_ROOT/backend/web"
cat > .env << EOF
ENVIRONMENT=test
PG_HOST=${PG_HOST}
PG_USER=${PG_USER}
PG_PASSWORD=${PG_PASSWORD}
PG_DB=${PG_DB}
PG_PORT=${PG_PORT:-5432}
LOG_LEVEL=DEBUG
REQUEST_ID_HEADER=X-Request-ID
DEFAULT_LIMIT=20
MAX_LIMIT=100
CACHE_TTL=300
EOF

# 创建task服务的.env文件
echo "📝 配置task服务环境变量..."
cd "$PROJECT_ROOT/backend/task"
cat > .env << EOF
ENVIRONMENT=test
PG_HOST=${PG_HOST}
PG_USER=${PG_USER}
PG_PASSWORD=${PG_PASSWORD}
PG_DB=${PG_DB}
PG_PORT=${PG_PORT:-5432}
LOG_LEVEL=DEBUG
EOF

echo "✓ 本地测试环境配置完成"

# 本地测试环境验证
echo "\n🔍 验证本地测试环境配置..."

# 检查.env文件是否创建成功
echo "检查配置文件:"
if [ -f "$PROJECT_ROOT/backend/web/.env" ]; then
    echo "✅ Web服务 .env 文件已创建"
else
    echo "❌ Web服务 .env 文件创建失败"
fi

if [ -f "$PROJECT_ROOT/backend/task/.env" ]; then
    echo "✅ Task服务 .env 文件已创建"
else
    echo "❌ Task服务 .env 文件创建失败"
fi

# 显示当前环境变量
echo "\n📊 当前测试环境配置:"
echo "   环境: test"
echo "   股票表: stock_test"
echo "   基金表: fund_test"
echo "   数据库: $PG_DB"
echo "   主机: $PG_HOST"

echo "\n✅ 本地测试环境配置完成！"
echo "\n💡 后续步骤:"
echo "   1. 确保已创建测试表 stock_test 和 fund_test"
echo "   2. 启动web服务: cd backend/web && python main.py"
echo "   3. 访问健康检查: http://localhost:8000/health"
echo "   4. 测试完成后使用 switch-env.sh 切换环境"
#!/bin/bash

# 生产环境部署脚本
# 使用方法: ./deploy-prod.sh

set -e  # 遇到错误立即退出

echo "========================================"
echo "开始部署到生产环境"
echo "========================================"

# 安全确认
read -p "⚠️  确认要部署到生产环境吗？(yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo "❌ 部署已取消"
    exit 1
fi

# 设置环境变量
export ENVIRONMENT=production
echo "✓ 环境设置: $ENVIRONMENT"

# 检查必要的环境变量
required_vars=("PG_HOST" "PG_USER" "PG_PASSWORD" "PG_DB")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ 错误: 环境变量 $var 未设置"
        echo "请设置以下环境变量:"
        echo "export PG_HOST=your-prod-db-host"
        echo "export PG_USER=your-prod-db-user"
        echo "export PG_PASSWORD=your-prod-db-password"
        echo "export PG_DB=your-prod-db-name"
        exit 1
    fi
done
echo "✓ 环境变量检查通过"

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/../.." && pwd )"

echo "项目根目录: $PROJECT_ROOT"

# 代码质量检查（可选）
echo "\n🔍 执行代码质量检查..."
cd "$PROJECT_ROOT/backend/web"
if command -v flake8 &> /dev/null; then
    echo "运行 flake8 检查..."
    flake8 . --max-line-length=120 --ignore=E501,W503 || echo "⚠️  代码风格检查发现问题，但继续部署"
else
    echo "⚠️  flake8 未安装，跳过代码风格检查"
fi

# 运行测试（如果存在）
if [ -f "test_main.py" ]; then
    echo "\n🧪 运行单元测试..."
    python -m pytest test_main.py -v || {
        echo "❌ 测试失败，停止部署"
        exit 1
    }
    echo "✓ 测试通过"
else
    echo "⚠️  未找到测试文件，跳过测试"
fi

# 部署 web 服务
echo "\n📦 部署 Web API 服务..."
cd "$PROJECT_ROOT/backend/web"

# 检查是否存在生产环境配置文件
if [ -f "serverless-prod.yml" ]; then
    echo "使用生产环境配置: serverless-prod.yml"
    serverless deploy --config serverless-prod.yml
else
    echo "⚠️  未找到 serverless-prod.yml，使用默认配置"
    # 临时设置环境变量并部署
    serverless deploy
fi

echo "✓ Web API 服务部署完成"

# 部署 task 服务
echo "\n📦 部署 Task 服务..."
cd "$PROJECT_ROOT/backend/task"

# 检查是否存在生产环境配置文件
if [ -f "serverless-task-prod.yml" ]; then
    echo "使用生产环境配置: serverless-task-prod.yml"
    serverless deploy --config serverless-task-prod.yml
else
    echo "⚠️  未找到 serverless-task-prod.yml，使用默认配置"
    serverless deploy
fi

echo "✓ Task 服务部署完成"

# 健康检查
echo "\n🔍 执行健康检查..."
if [ ! -z "$WEB_API_URL" ]; then
    echo "检查 Web API 健康状态: $WEB_API_URL"
    
    # 等待服务启动
    echo "等待服务启动..."
    sleep 10
    
    # 执行健康检查
    for i in {1..5}; do
        echo "健康检查尝试 $i/5..."
        response=$(curl -s "$WEB_API_URL/" || echo "")
        if [[ $response == *"healthy"* ]]; then
            echo "✓ 服务健康检查通过"
            echo "响应: $response"
            break
        else
            echo "⚠️  健康检查失败，等待重试..."
            sleep 5
        fi
        
        if [ $i -eq 5 ]; then
            echo "❌ 健康检查失败，请手动验证服务状态"
        fi
    done
else
    echo "⚠️  WEB_API_URL 未设置，跳过健康检查"
    echo "部署完成后，请手动访问 API 网关地址进行验证"
fi

# 部署后通知（可选）
if [ ! -z "$SLACK_WEBHOOK_URL" ]; then
    echo "\n📢 发送部署通知..."
    curl -X POST -H 'Content-type: application/json' \
        --data '{"text":"🚀 生产环境部署完成\n环境: production\n时间: '$(date)'\n版本: 2.0.0"}' \
        $SLACK_WEBHOOK_URL
fi

echo "\n========================================"
echo "✅ 生产环境部署完成！"
echo "========================================"
echo "环境信息:"
echo "- 环境: $ENVIRONMENT"
echo "- 股票表: stock_info"
echo "- 基金表: fund_info"
echo "- 数据库: $PG_DB"
echo "- 部署时间: $(date)"
echo "\n请进行以下验证:"
echo "1. 访问 API 健康检查接口"
echo "2. 验证股票和基金数据查询功能"
echo "3. 检查监控和告警配置"
echo "4. 验证缓存和限流功能"
echo "========================================"
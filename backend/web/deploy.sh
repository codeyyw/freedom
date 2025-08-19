#!/bin/bash

# 股票基金云函数部署脚本

set -e

echo "=== 股票基金云函数部署脚本 ==="

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请先安装Python3"
    exit 1
fi

# 检查pip
if ! command -v pip3 &> /dev/null; then
    echo "错误: 未找到pip3，请先安装pip3"
    exit 1
fi

# 创建虚拟环境（可选）
read -p "是否创建虚拟环境? (y/n): " create_venv
if [[ $create_venv == "y" || $create_venv == "Y" ]]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
    source venv/bin/activate
    echo "虚拟环境已激活"
fi

# 安装依赖
echo "安装Python依赖..."
pip3 install -r requirements.txt

# 检查环境变量
echo "检查环境变量..."
required_vars=("PG_HOST" "PG_USER" "PG_PASSWORD" "PG_DB")
missing_vars=()

for var in "${required_vars[@]}"; do
    if [[ -z "${!var}" ]]; then
        missing_vars+=("$var")
    fi
done

if [[ ${#missing_vars[@]} -gt 0 ]]; then
    echo "警告: 以下环境变量未设置:"
    printf '%s\n' "${missing_vars[@]}"
    echo "请设置这些环境变量后再运行服务"
    echo "可以运行: source ../task/env.sh"
fi

# 选择部署方式
echo ""
echo "请选择部署方式:"
echo "1. 本地测试运行"
echo "2. 创建部署包"
echo "3. Serverless Framework部署"
echo "4. 退出"

read -p "请输入选择 (1-4): " choice

case $choice in
    1)
        echo "启动本地测试服务..."
        echo "服务将在 http://localhost:9000 启动"
        echo "按 Ctrl+C 停止服务"
        python3 main.py
        ;;
    2)
        echo "创建部署包..."
        # 创建临时目录
        temp_dir="deploy_package_$(date +%Y%m%d_%H%M%S)"
        mkdir -p "$temp_dir"
        
        # 复制文件
        cp main.py requirements.txt README.md "$temp_dir/"
        
        # 安装依赖到包目录
        pip3 install -r requirements.txt -t "$temp_dir/"
        
        # 创建zip包
        cd "$temp_dir"
        zip -r "../stock-fund-api.zip" .
        cd ..
        
        # 清理临时目录
        rm -rf "$temp_dir"
        
        echo "部署包已创建: stock-fund-api.zip"
        echo "可以上传到云函数平台进行部署"
        ;;
    3)
        if ! command -v serverless &> /dev/null; then
            echo "错误: 未找到serverless命令，请先安装Serverless Framework"
            echo "安装命令: npm install -g serverless"
            exit 1
        fi
        
        echo "使用Serverless Framework部署..."
        echo "请确保已配置AWS凭证"
        read -p "继续部署? (y/n): " confirm
        
        if [[ $confirm == "y" || $confirm == "Y" ]]; then
            serverless deploy
            echo "部署完成！"
        else
            echo "部署已取消"
        fi
        ;;
    4)
        echo "退出部署脚本"
        exit 0
        ;;
    *)
        echo "无效选择，退出"
        exit 1
        ;;
esac

echo "部署脚本执行完成！"
#!/bin/bash
# 基金同步系统环境变量配置
# 使用方法: source env.sh

export PYTHONUNBUFFERED=1
export PG_DB=tushare
export PG_HOST=rm-cn-yjp4duh2d00013.rwlb.rds.aliyuncs.com
export PG_HOST_OUT=rm-cn-yjp4duh2d00013fo.rwlb.rds.aliyuncs.com
export PG_PASSWORD=Yyw970512
export PG_PORT=5432
export PG_USER=yuanyiwei

echo "环境变量设置完成！"
echo "数据库连接信息："
echo "  数据库: $PG_DB"
echo "  主机: $PG_HOST_OUT"
echo "  用户: $PG_USER"
echo "  端口: $PG_PORT"
echo ""
echo "现在可以运行: python run_sync.py"

# 股票基金云函数服务

这是一个整合了股票和基金查询功能的云函数服务，基于Flask框架开发。

## 功能特性

- **股票信息查询** (`/stockinfo`): 支持按市场、代码、名称、状态等条件查询股票信息
- **基金信息查询** (`/fundinfo`): 支持按基金代码、名称、类型、状态等条件查询基金信息
- **健康检查** (`/`): 服务状态检查和API文档

## API接口

### 1. 健康检查
```
GET /
```
返回服务状态和可用接口列表。

### 2. 股票信息查询
```
GET /stockinfo
```

**查询参数:**
- `market`: 市场代码（精确匹配）
- `symbol`: 股票代码（精确匹配）
- `name`: 股票名称（模糊匹配，支持中文名和英文名）
- `status`: 状态（默认为'L'）
- `limit`: 返回记录数限制（默认500）
- `order`: 排序方式（asc/desc，按更新时间排序）

**示例:**
```bash
# 查询所有上海市场的股票
curl "http://localhost:9000/stockinfo?market=SH&limit=10"

# 按名称模糊查询
curl "http://localhost:9000/stockinfo?name=平安&limit=5"
```

### 3. 基金信息查询
```
GET /fundinfo
```

**查询参数:**
- `code`: 基金代码（精确匹配）
- `name`: 基金名称（模糊匹配）
- `type`: 基金类型（精确匹配）
- `status`: 状态（默认为'L'）
- `limit`: 返回记录数限制（默认500）
- `order`: 排序方式（asc/desc，按更新时间排序）

**示例:**
```bash
# 查询指定基金代码
curl "http://localhost:9000/fundinfo?code=000001"

# 按名称模糊查询
curl "http://localhost:9000/fundinfo?name=货币&limit=10"
```

## 环境变量配置

服务需要以下环境变量:

```bash
# 数据库连接配置
export PG_HOST="your-postgres-host"
export PG_HOST_OUT="your-postgres-host-for-fund"  # 基金数据库主机
export PG_PORT="5432"
export PG_USER="your-username"
export PG_PASSWORD="your-password"
export PG_DB="your-database"

# 请求ID头部字段名（可选）
export REQUEST_ID_HEADER="X-Request-ID"
```

## 本地开发

1. 安装依赖:
```bash
pip install -r requirements.txt
```

2. 设置环境变量:
```bash
source ../task/env.sh  # 或手动设置上述环境变量
```

3. 运行服务:
```bash
python main.py
```

服务将在 `http://localhost:9000` 启动。

## 云函数部署

### 腾讯云SCF部署

1. 将整个目录打包为zip文件
2. 在腾讯云控制台创建云函数
3. 上传代码包
4. 设置入口函数为 `main.main`
5. 配置环境变量
6. 设置触发器（API网关）

### 阿里云函数计算部署

1. 使用Fun工具或控制台部署
2. 设置Handler为 `main.main`
3. 配置环境变量和触发器

### AWS Lambda部署

1. 安装serverless框架或使用AWS CLI
2. 配置serverless.yml或使用控制台
3. 设置Handler为 `main.main`

## 数据库表结构

### stock_info表
- `symbol`: 股票代码
- `name`: 英文名称
- `cname`: 中文名称
- `market`: 市场代码
- `status`: 状态
- `update_time`: 更新时间

### fund_info表
- `fund_code`: 基金代码
- `fund_name`: 基金名称
- `fund_type`: 基金类型
- `status`: 状态
- `update_time`: 更新时间

## 日志

服务使用Python标准logging模块，日志级别为INFO。每个请求都会记录:
- 请求URL和参数
- 执行的SQL语句
- 返回的记录数
- 异常信息（如有）

## 错误处理

- 数据库连接错误: 返回500状态码和错误信息
- 参数验证错误: 使用默认值或返回400状态码
- SQL执行错误: 返回500状态码和错误信息

所有错误都会记录到日志中，便于调试和监控。
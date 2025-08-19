# 环境配置说明

本项目支持多环境部署，通过环境变量 `ENVIRONMENT` 来区分不同的运行环境。

## 环境类型

### 1. 生产环境 (production)
- **ENVIRONMENT**: `production` 或不设置（默认值）
- **表名**: 使用原始表名
  - 股票表: `stock_info`
  - 基金表: `fund_info`

### 2. 测试环境 (test)
- **ENVIRONMENT**: `test`
- **表名**: 使用测试表名
  - 股票表: `stock_test`
  - 基金表: `fund_test`

### 3. 开发环境 (development)
- **ENVIRONMENT**: `development`
- **表名**: 使用开发表名
  - 股票表: `stock_info_dev`
  - 基金表: `fund_info_dev`

## 云函数部署配置

### 腾讯云 SCF 配置示例

#### 生产环境
```yaml
# serverless-prod.yml
service: stock-fund-api-prod
provider:
  name: tencent
  runtime: Python3.12
  region: ap-guangzhou
  environment:
    ENVIRONMENT: production
    PG_HOST: your-prod-db-host
    PG_USER: your-prod-db-user
    PG_PASSWORD: your-prod-db-password
    PG_DB: your-prod-db-name
```

#### 测试环境
```yaml
# serverless-test.yml
service: stock-fund-api-test
provider:
  name: tencent
  runtime: Python3.12
  region: ap-guangzhou
  environment:
    ENVIRONMENT: test
    PG_HOST: your-test-db-host
    PG_USER: your-test-db-user
    PG_PASSWORD: your-test-db-password
    PG_DB: your-test-db-name
```

### 阿里云函数计算配置示例

#### 生产环境
```yaml
# template-prod.yml
ROSTemplateFormatVersion: '2015-09-01'
Transform: 'Aliyun::Serverless-2018-04-03'
Resources:
  stock-fund-service-prod:
    Type: 'Aliyun::Serverless::Service'
    Properties:
      Description: 股票基金API服务-生产环境
    web-api-prod:
      Type: 'Aliyun::Serverless::Function'
      Properties:
        Runtime: python3.12
        EnvironmentVariables:
          ENVIRONMENT: production
          PG_HOST: your-prod-db-host
          PG_USER: your-prod-db-user
          PG_PASSWORD: your-prod-db-password
          PG_DB: your-prod-db-name
```

#### 测试环境
```yaml
# template-test.yml
ROSTemplateFormatVersion: '2015-09-01'
Transform: 'Aliyun::Serverless-2018-04-03'
Resources:
  stock-fund-service-test:
    Type: 'Aliyun::Serverless::Service'
    Properties:
      Description: 股票基金API服务-测试环境
    web-api-test:
      Type: 'Aliyun::Serverless::Function'
      Properties:
        Runtime: python3.12
        EnvironmentVariables:
          ENVIRONMENT: test
          PG_HOST: your-test-db-host
          PG_USER: your-test-db-user
          PG_PASSWORD: your-test-db-password
          PG_DB: your-test-db-name
```

## 本地开发配置

### 本地测试环境

#### 快速启动
```bash
# 1. 配置测试环境
cd backend/deploy-scripts
./deploy-test.sh

# 2. 启动测试服务
./start-local-test.sh
```

#### 手动配置
```bash
# 设置环境变量
export ENVIRONMENT=test
export PG_HOST=localhost
export PG_USER=your_username
export PG_PASSWORD=your_password
export PG_DB=your_database
export PG_PORT=5432

# 启动服务
cd backend/web
python main.py
```

### 环境变量设置

#### Linux/macOS
```bash
# 测试环境
export ENVIRONMENT=test
export PG_HOST=localhost
export PG_USER=postgres
export PG_PASSWORD=your-password
export PG_DB=your-test-db

# 运行服务
python main.py
```

#### Windows
```cmd
# 测试环境
set ENVIRONMENT=test
set PG_HOST=localhost
set PG_USER=postgres
set PG_PASSWORD=your-password
set PG_DB=your-test-db

# 运行服务
python main.py
```

### .env 文件配置（推荐）

创建 `.env` 文件：
```env
# 测试环境配置
ENVIRONMENT=test
PG_HOST=localhost
PG_PORT=5432
PG_USER=postgres
PG_PASSWORD=your-password
PG_DB=your-test-db
PG_HOST_OUT=localhost

# 应用配置
DEFAULT_LIMIT=500
MAX_LIMIT=1000
CACHE_TTL=300
LOG_LEVEL=DEBUG
```

## 部署脚本示例

### 测试环境部署
```bash
#!/bin/bash
# deploy-test.sh

echo "部署到测试环境..."

# 设置环境变量
export ENVIRONMENT=test

# 部署 web 服务
cd backend/web
serverless deploy --config serverless-test.yml

# 部署 task 服务
cd ../task
serverless deploy --config serverless-task-test.yml

echo "测试环境部署完成！"
```

### 生产环境部署
```bash
#!/bin/bash
# deploy-prod.sh

echo "部署到生产环境..."

# 设置环境变量
export ENVIRONMENT=production

# 部署 web 服务
cd backend/web
serverless deploy --config serverless-prod.yml

# 部署 task 服务
cd ../task
serverless deploy --config serverless-task-prod.yml

echo "生产环境部署完成！"
```

## 数据库表创建

在部署前，请确保已在对应环境的数据库中创建了相应的表：

### 测试环境
```sql
-- 执行测试表创建脚本
\i stock_test_table.sql
\i fund_test_table.sql
```

### 生产环境
```sql
-- 执行生产表创建脚本
\i stock_info_table.sql
\i fund_info_table.sql
```

## 注意事项

1. **环境隔离**: 确保不同环境使用不同的数据库或表，避免数据混淆
2. **配置安全**: 生产环境的数据库密码等敏感信息应使用云平台的密钥管理服务
3. **监控告警**: 为不同环境设置不同的监控和告警策略
4. **日志级别**: 测试环境可使用 DEBUG 级别，生产环境建议使用 INFO 或 WARN 级别
5. **资源配置**: 生产环境应配置更高的内存和超时时间

## 环境切换验证

部署后可通过健康检查接口验证环境配置：

```bash
# 检查当前环境
curl https://your-api-domain/health

# 响应示例
{
  "status": "healthy",
  "service": "股票基金云函数服务",
  "version": "2.0.0",
  "environment": "test",  # 当前环境
  "tables": {
    "stock": "stock_test",  # 当前使用的表名
    "fund": "fund_test"
  }
}
```
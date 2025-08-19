# 股票数据同步系统

## 项目概述

本系统是一个高效的股票实时行情数据同步工具，支持A股、港股、美股三大市场的数据获取、清洗和存储。系统具备智能市场状态检测、批量数据处理、错误恢复等特性，确保数据的实时性和准确性。

## 项目结构

```
stocksync/
├── index.py              # 主程序入口
├── data_processor.py     # 数据处理核心模块（新增）
├── market_status.py      # 市场开盘状态检测模块（重命名）
├── stock_cleaners.py     # 股票数据清洗模块
├── db_operations.py      # 数据库操作模块
├── config.py             # 配置文件
├── 启动说明.txt          # 启动说明
└── README.md             # 项目文档
```

## 核心功能

### 1. 多市场支持

#### A股市场
- **交易时间**: 09:30-11:30, 13:00-15:00 (UTC+8)
- **数据源**: akshare.stock_zh_a_spot_em()
- **数据字段**: 代码、名称、最新价、涨跌额、涨跌幅、买入价、卖出价、昨收、今开、最高、最低、成交量、成交额、时间戳

#### 港股市场
- **交易时间**: 09:30-12:00, 13:00-16:00 (UTC+8)
- **数据源**: akshare.stock_hk_spot_em()
- **数据字段**: 代码、中文名称、英文名称、最新价、涨跌额、涨跌幅、买一、卖一、昨收、今开、最高、最低、成交量、成交额

#### 美股市场
- **交易时间**: 
  - 夏令时: 21:30-04:00 (UTC+8)
  - 冬令时: 22:30-05:00 (UTC+8)
- **数据源**: akshare.stock_us_spot_em()
- **数据字段**: 代码、名称、最新价、涨跌幅等

### 2. 智能市场检测

系统具备智能的市场开盘状态检测功能：

```python
# 检测A股是否开盘
is_a_stock_market_open()

# 检测港股是否开盘
is_hk_stock_market_open()

# 检测美股是否开盘（自动处理夏令时）
is_us_stock_market_open()

# 统一市场状态检测
check_market_open_status()
```

### 3. 数据清洗处理

每个市场都有专门的数据清洗函数：

- `clean_a_stock(df)`: A股数据清洗
- `clean_hk_stock(df)`: 港股数据清洗  
- `clean_us_stock(df)`: 美股数据清洗

清洗过程包括：
- 数据类型转换
- 空值处理
- 字段标准化
- 时间戳生成

### 4. 高效数据库操作

- **批量插入**: 新股票记录批量写入
- **批量更新**: 现有股票价格批量更新
- **状态管理**: 自动标记删除失效股票
- **并发处理**: 支持多线程数据库操作

## 技术架构

### 数据流程

```
市场开盘检测 → 数据获取 → 数据清洗 → 数据库比对 → 批量更新/插入
```

### 核心组件

1. **数据获取层**: 基于akshare的API调用
2. **数据处理层**: StockDataProcessor类封装的数据处理逻辑
3. **数据存储层**: SQLAlchemy数据库操作
4. **市场检测层**: 智能市场开盘状态检测
4. **监控层**: 日志记录和错误处理

### 性能优化

- **批处理**: 1500条记录/批次，减少数据库I/O
- **并发处理**: 2个线程并行处理
- **连接池**: 数据库连接复用
- **重试机制**: 网络异常自动重试

## 安装和配置

### 环境要求

- Python 3.7+
- PostgreSQL 数据库
- 稳定的网络连接

### 依赖安装

```bash
pip install akshare sqlalchemy psycopg2-binary pandas
```

### 环境变量配置

```bash
export PG_USER=your_username
export PG_PASSWORD=your_password
export PG_HOST_OUT=your_host
export PG_DB=your_database
export PG_PORT=5432
```

### 数据库表结构

```sql
CREATE TABLE stock_info (
    symbol VARCHAR(20) NOT NULL,
    cname VARCHAR(100),
    name VARCHAR(100),
    category VARCHAR(50),
    category_id INTEGER,
    market VARCHAR(20) NOT NULL,
    status CHAR(1) DEFAULT 'L',
    price DECIMAL(10,4),
    diff DECIMAL(10,4),
    chg DECIMAL(8,4),
    preclose DECIMAL(10,4),
    open DECIMAL(10,4),
    high DECIMAL(10,4),
    low DECIMAL(10,4),
    amplitude DECIMAL(8,4),
    volume BIGINT,
    turnover DECIMAL(15,2),
    mktcap DECIMAL(15,2),
    pe DECIMAL(10,2),
    best_bid_price DECIMAL(10,4),
    best_ask_price DECIMAL(10,4),
    datetime TIMESTAMP,
    PRIMARY KEY (symbol, market)
);
```

## 使用方法

### 基本使用

```bash
# 1. 配置环境变量
source test/env.sh

# 2. 运行测试
python test/test_imports.py

# 3. 启动同步
python index.py
```

### 模块化使用

```python
# 使用StockDataProcessor类
from data_processor import StockDataProcessor

# 初始化数据处理器
processor = StockDataProcessor()

# 收集所有股票数据
stats = processor.collect_all_stock_data()
print(f"处理统计: {stats}")

# 获取数据库连接字符串
conn_str = processor.get_db_connection_string()

# 格式化持续时间
duration = processor.format_duration(10.5)
print(f"耗时: {duration}")
```

### 高级配置

在 `config.py` 中可以调整：

```python
# 市场配置
MARKET_CONFIGS = {
    "A股": {
        "api_func": "stock_zh_a_spot_em",
        "clean_func": "clean_a_stock",
        "check_func": "is_a_stock_market_open",
        "batch_size": 1500,
        "concurrency": 2
    },
    "港股": {
        "api_func": "stock_hk_spot_em",
        "clean_func": "clean_hk_stock",
        "check_func": "is_hk_stock_market_open",
        "batch_size": 1500,
        "concurrency": 2
    },
    "美股": {
        "api_func": "stock_us_spot_em",
        "clean_func": "clean_us_stock",
        "check_func": "is_us_stock_market_open",
        "batch_size": 1500,
        "concurrency": 2
    }
}

# 数据库配置
DB_CONFIG = {
    "batch_size": 1500,
    "max_workers": 2,
    "max_retry": 3,
    "retry_delay": 5
}

# 市场检查配置
MARKET_CHECK_CONFIG = {
    "check_hours_before": 2,
    "timezone_offset": 8  # 北京时间
}
```

## 监控和日志

### 日志格式

```
[2024-01-15 09:30:00] INFO MainThread [A股] 开始获取实时行情数据...
[2024-01-15 09:30:05] INFO MainThread [A股] 获取到 4500 条记录
[2024-01-15 09:30:08] INFO MainThread [A股] 新增记录: 50, 更新记录: 4400, 删除记录: 10
[2024-01-15 09:30:10] INFO MainThread [A股] 数据库同步完成，耗时: 10.2345 秒
```

### 性能指标

- **数据获取速度**: ~5000条/秒
- **数据清洗速度**: ~10000条/秒
- **数据库写入速度**: ~3000条/秒
- **内存使用**: <100MB

## 测试

### 运行测试套件

```bash
cd test/

# 模块导入测试
python test_imports.py

# 集成测试
python test_integration.py

# 性能测试
python performance_test.py

# 市场状态测试
python test_market_status.py

# 数据清洗测试
python test_data_cleaning.py
```

### 调试工具

```bash
# akshare API调试
python debug_akshare.py
```

## 故障排除

### 常见问题

1. **连接超时**
   - 检查网络连接
   - 验证数据库配置
   - 增加重试次数

2. **数据为空**
   - 确认市场开盘状态
   - 检查API限制
   - 验证数据源可用性

3. **导入错误**
   - 检查Python版本
   - 验证依赖包安装
   - 确认模块路径

4. **性能问题**
   - 调整批处理大小
   - 优化并发线程数
   - 检查数据库性能

### 调试步骤

1. 运行 `test_imports.py` 检查模块导入
2. 运行 `test_market_status.py` 检查市场状态
3. 运行 `debug_akshare.py` 检查数据源
4. 检查日志文件定位具体错误

## 扩展开发

### 添加新市场

1. 在 `share_open.py` 中添加开盘检测函数
2. 在 `stock_cleaners.py` 中添加数据清洗函数
3. 在 `config.py` 中添加市场配置
4. 在 `index.py` 中添加市场处理逻辑

### 自定义数据处理

```python
def custom_clean_function(df):
    # 自定义数据清洗逻辑
    return cleaned_df
```

## 版本历史

- **v1.0**: 初始版本
  - 支持A股、港股、美股数据同步
  - 模块化架构设计，包含数据处理核心模块
  - 智能市场开盘状态检测
  - StockDataProcessor类封装数据处理逻辑
  - 批量数据库操作优化
  - 完善的错误处理和重试机制
  - 基于北京时间的准确时区处理

## 许可证

本项目采用 MIT 许可证。

## 贡献

欢迎提交 Issue 和 Pull Request 来改进项目。

## 联系方式

如有问题或建议，请通过以下方式联系：
- 提交 GitHub Issue
- 发送邮件至项目维护者

---

**注意**: 本系统仅用于数据同步，不构成投资建议。使用时请遵守相关法律法规和交易所规定。
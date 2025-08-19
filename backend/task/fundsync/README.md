# 基金数据同步系统

## 项目结构

```
fundsync/
├── syncfund.py          # 主程序入口
├── data_processor.py    # 数据处理模块
├── db_operations.py     # 数据库操作模块
├── config.py            # 配置文件
├── test/                # 测试目录
│   ├── debug_akshare.py       # akshare调试脚本
│   ├── performance_test.py    # 性能测试脚本
│   ├── test_fixed_function.py # 功能测试脚本
│   ├── test_imports.py        # 模块导入测试脚本
│   ├── test_integration.py    # 集成测试脚本
│   ├── test_new_function.py   # 新功能测试脚本
│   └── env.sh                 # 环境变量配置脚本
├── 启动说明.txt         # 启动说明
└── README.md            # 说明文档
```

## 功能说明

本系统实现了基金数据的自动同步功能，主要特点：

1. **数据整合**：整合场内基金、开放基金、货币基金、欧美QDII、亚洲QDII等不同类型基金数据
2. **重复处理**：自动识别并处理重复编码，以QDII数据为准
3. **强制更新**：每次运行都会强制更新所有现有基金的最新价格数据
4. **数据库同步**：自动更新数据库中的基金信息，包括新增、更新和删除操作
5. **优化日志**：集中记录空价格基金编码，提高日志可读性
6. **错误处理**：具备完善的错误处理和重试机制

## 核心模块

### 1. 主程序 (syncfund.py)
- 程序入口点
- 协调各个模块的执行流程
- 管理数据库连接
- 强制更新所有基金价格数据

### 2. 数据处理模块 (data_processor.py)
- 负责从各种API获取基金数据
- 过滤价格不为空的数据，并记录空价格基金编码集合
- 处理数据整合和重复编码逻辑
- 分析数据差异
- 优化日志输出，集中显示空价格基金信息

### 3. 数据库操作模块 (db_operations.py)
- 封装所有数据库操作
- 支持批量插入、更新和删除操作
- 提供事务管理
- 多线程并发处理，提高数据库操作效率
- 智能处理空集合，避免不必要的数据库操作

### 4. 配置文件 (config.py)
- 集中管理基金类型配置
- 数据库和日志配置参数
- 便于维护和修改

## 使用方法

### 环境要求
```bash
pip install akshare sqlalchemy psycopg2-binary
```

### 环境变量配置
```bash
export PG_USER="your_username"
export PG_PASSWORD="your_password"
export PG_HOST_OUT="your_host"
export PG_PORT="5432"
export PG_DB="your_database"

# 使用环境配置脚本
source test/env.sh 
```

### 运行程序
```bash
cd fundsync
python syncfund.py
```

### 运行测试
```bash
cd test
python test_integration.py
```

### 模块化使用

```python
# 使用FundDataProcessor类
from data_processor import FundDataProcessor

# 初始化数据处理器
processor = FundDataProcessor()

# 收集所有基金数据
all_funds = processor.collect_all_fund_data()
print(f"收集到 {len(all_funds)} 只基金")

# 分析数据差异
to_insert, to_update, to_delete = processor.analyze_data_differences(all_funds)
print(f"新增: {len(to_insert)}, 更新: {len(to_update)}, 删除: {len(to_delete)}")

# 执行数据库同步
from db_operations import FundDatabase
db = FundDatabase()
db.sync_fund_data(to_insert, to_update, to_delete)
```

## 技术架构

### 数据流程

```
数据收集 → 数据过滤 → 重复处理 → 数据整合 → 强制更新 → 数据库同步
```

1. **数据收集**：从各个API获取不同类型的基金数据
2. **数据过滤**：过滤出价格不为空的基金记录，并记录空价格基金编码集合
3. **重复处理**：识别重复编码，以QDII数据为准
4. **数据整合**：合并所有有效数据形成最终集合
5. **强制更新**：无论是否有新增或删除基金，都会更新现有基金的最新价格
6. **数据库更新**：执行批量数据库操作，包括标记删除、插入新基金、更新现有基金价格

### 核心组件

1. **数据获取层**: 基于akshare的多源API调用
2. **数据处理层**: FundDataProcessor类封装的数据处理逻辑
3. **数据存储层**: SQLAlchemy数据库操作
4. **配置管理层**: 统一的配置文件管理

## 配置说明

### 基金类型配置
```python
FUND_TYPES = {
    "开放基金": {
        "api_func": "ak.fund_open_fund_daily_em",
        "concurrency": 4,
        "price_column_pattern": "单位净值"
    },
    # ... 其他类型
}
```

### 数据库配置
```python
DB_CONFIG = {
    "batch_size": 1500,    # 批处理大小
    "max_retry": 3,        # 最大重试次数
    "retry_delay": 5       # 重试延迟（秒）
}
```

## 优势特点

1. **模块化设计**：代码结构清晰，便于维护和扩展
2. **配置化管理**：通过配置文件管理各种参数，无需修改代码
3. **错误处理**：完善的异常处理和重试机制
4. **性能优化**：支持批量操作和多线程并发处理
5. **日志记录**：详细的日志记录，便于问题排查
6. **强制更新**：确保每次运行都会更新现有基金的最新价格
7. **测试完备**：包含完整的测试套件，确保代码质量

## 版本历史

### v1.0 (初始版本)
- 支持场内基金、开放基金、货币基金、欧美QDII、亚洲QDII等多类型基金数据同步
- 模块化架构设计，包含数据处理和数据库操作模块
- 智能重复处理：自动识别并处理重复编码，以QDII数据为准
- 强制更新机制：确保每次都更新现有基金价格
- 多线程数据库操作，提高处理效率
- 完善的错误处理和重试机制
- 数据完整性检查：必须所有数据源都成功才能与数据库交互
- 优化日志输出：集中记录空价格基金编码

## 注意事项

1. 确保数据库连接参数正确配置
2. 网络环境稳定，避免API调用失败
3. 定期检查日志，监控同步状态
4. 建议在非交易时间执行同步操作
5. 测试文件已移至 `test/` 目录，运行测试前请切换到该目录
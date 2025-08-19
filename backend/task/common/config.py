# -*- coding: utf-8 -*-
"""
统一配置管理
"""
import os

# 环境配置
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'production')  # production, test, development

# 表名配置函数
def get_table_name(base_table: str) -> str:
    """根据环境获取表名"""
    if ENVIRONMENT == 'test':
        return f"{base_table.replace('_info', '_test')}"
    elif ENVIRONMENT == 'development':
        return f"{base_table}_dev"
    else:
        return base_table  # production环境使用原表名

# 动态表名
STOCK_TABLE = get_table_name('stock_info')
FUND_TABLE = get_table_name('fund_info')

# 统一日志配置
LOG_CONFIG = {
    "level": "INFO",
    "format": "[%(asctime)s] %(levelname)s %(threadName)s %(message)s",
    "datefmt": "%Y-%m-%d %H:%M:%S"
}

# 统一数据库配置
DB_CONFIG = {
    "batch_size": 2000,       # 默认批处理大小
    "max_retry": 3,        # 默认最大重试次数
    "retry_delay": 3,                                   # 默认重试延迟（秒）
    "timeout": 30             # 默认超时时间
}

# 股票模块特定配置
STOCK_CONFIG = {
    "batch_size": 2000,        # 股票批处理大小
    "max_retry": 3,         # 股票最大重试次数
    "retry_delay": 5,     # 股票重试延迟
    "timeout": 30,            # 股票超时时间
    "market_check": {
        "check_hours_before": 2,  # 检查几小时前是否开盘
        "timezone_offset": 8         # 时区偏移（北京时间）
    }
}

# 基金模块特定配置
FUND_CONFIG = {
    "batch_size": 2000,         # 基金批处理大小
    "max_workers": 6,       # 基金数据库操作的最大线程数
    "max_retry": 3,         # 基金最大重试次数
    "retry_delay": 5,     # 基金重试延迟
}

# 重试配置
RETRY_CONFIG = {
    "max_retry": 3,
    "retry_delay": 2,
    "timeout": 30
}

# 市场配置
MARKET_CONFIGS = {
    "A股": {
        "api_func": "stock_zh_a_spot",
        "concurrency": 2,
        "batch_size": 2000
    },
    "港股": {
        "api_func": "stock_hk_spot", 
        "concurrency": 1,
        "batch_size": 2000
    },
    "美股": {
         "api_func": "stock_us_spot",
         "concurrency": 4,
         "batch_size": 4000
     }
}

# 基金类型配置
FUND_TYPES = {
    "开放基金": {
        "api_func": "fund_open_fund_daily_em",
        "concurrency": 1,
        "price_column_pattern": "单位净值"
    },
    "货币基金": {
        "api_func": "fund_money_fund_daily_em", 
        "concurrency": 1,
        "price_column_pattern": "万份收益"
    },
    "场内基金": {
        "api_func": "fund_etf_fund_daily_em",
        "concurrency": 1,
        "price_column_pattern": "单位净值"
    },
    "欧美QDII": {
        "api_func": "qdii_e_index_jsl",
        "concurrency": 1,
        "price_column_pattern": "现价"
    },
    "亚洲QDII": {
        "api_func": "qdii_a_index_jsl", 
        "concurrency": 1,
        "price_column_pattern": "现价"
    }
}

def get_config(module_type: str = 'default'):
    """获取指定模块的配置"""
    if module_type == 'stock':
        return {
            'db_config': STOCK_CONFIG,
            'log_config': LOG_CONFIG,
            'retry_config': RETRY_CONFIG,
            'market_configs': MARKET_CONFIGS
        }
    elif module_type == 'fund':
        return {
            'db_config': FUND_CONFIG,
            'log_config': LOG_CONFIG,
            'fund_types': FUND_TYPES
        }
    else:
        return {
            'db_config': DB_CONFIG,
            'log_config': LOG_CONFIG,
            'retry_config': RETRY_CONFIG
        }
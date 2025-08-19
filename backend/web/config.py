import os
from typing import Optional

class Config:
    """应用配置管理类"""
    
    def __init__(self):
        self.load_config()
    
    def load_config(self):
        """加载配置"""
        # 环境配置
        self.ENVIRONMENT = os.environ.get('ENVIRONMENT', 'production')  # production, test, development
        
        # 数据库配置
        self.PG_HOST = os.environ.get('PG_HOST')
        self.PG_HOST_OUT = os.environ.get('PG_HOST_OUT')
        self.PG_PORT = int(os.environ.get('PG_PORT', 5432))
        self.PG_USER = os.environ.get('PG_USER')
        self.PG_PASSWORD = os.environ.get('PG_PASSWORD')
        self.PG_DB = os.environ.get('PG_DB')
        
        # 表名配置（根据环境自动切换）
        self.STOCK_TABLE = self._get_table_name('stock_info')
        self.FUND_TABLE = self._get_table_name('fund_info')
        
        # 应用配置
        self.REQUEST_ID_HEADER = os.environ.get('REQUEST_ID_HEADER', 'X-Request-ID')
        self.DEFAULT_LIMIT = int(os.environ.get('DEFAULT_LIMIT', 500))
        self.MAX_LIMIT = int(os.environ.get('MAX_LIMIT', 1000))
        
        # 日志配置
        self.LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
        
        # 缓存配置
        self.CACHE_TTL = int(os.environ.get('CACHE_TTL', 300))  # 5分钟
    
    def _get_table_name(self, base_table: str) -> str:
        """根据环境获取表名"""
        if self.ENVIRONMENT == 'test':
            return f"{base_table.replace('_info', '_test')}"
        elif self.ENVIRONMENT == 'development':
            return f"{base_table}_dev"
        else:
            return base_table  # production环境使用原表名
        
    def validate(self) -> list:
        """验证必需的配置项"""
        required_configs = [
            ('PG_HOST', self.PG_HOST),
            ('PG_USER', self.PG_USER),
            ('PG_PASSWORD', self.PG_PASSWORD),
            ('PG_DB', self.PG_DB)
        ]
        
        missing = []
        for name, value in required_configs:
            if not value:
                missing.append(name)
        
        return missing
    
    def get_stock_db_config(self) -> dict:
        """获取股票数据库配置"""
        return {
            'host': self.PG_HOST,
            'port': self.PG_PORT,
            'user': self.PG_USER,
            'password': self.PG_PASSWORD,
            'dbname': self.PG_DB
        }
    
    def get_fund_db_config(self) -> dict:
        """获取基金数据库配置"""
        return {
            'host': self.PG_HOST_OUT or self.PG_HOST,
            'port': self.PG_PORT,
            'user': self.PG_USER,
            'password': self.PG_PASSWORD,
            'dbname': self.PG_DB
        }

# 全局配置实例
config = Config()
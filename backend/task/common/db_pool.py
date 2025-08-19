#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库连接池管理器
"""

import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
from threading import Lock
from .config import DB_CONFIG

logger = logging.getLogger(__name__)

class DatabaseConnectionPool:
    """数据库连接池管理器"""
    
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        """单例模式确保全局只有一个连接池"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """初始化连接池"""
        if hasattr(self, '_initialized'):
            return
        
        self._initialized = True
        self._engine = None
        self._create_engine()
    
    def _get_db_connection_string(self) -> str:
        """获取数据库连接字符串"""
        pg_host = os.environ.get('PG_HOST', 'localhost')
        pg_port = os.environ.get('PG_PORT', '5432')
        pg_user = os.environ.get('PG_USER', 'postgres')
        pg_password = os.environ.get('PG_PASSWORD', '')
        pg_db = os.environ.get('PG_DB', 'postgres')
        
        return f"postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}"
    
    def _create_engine(self):
        """创建数据库引擎和连接池"""
        try:
            connection_string = self._get_db_connection_string()
            
            # 使用默认连接池配置
            pool_config = {
                'pool_size': 20,
                'max_overflow': 10,
                        'pool_pre_ping': True,
                        'pool_recycle': 3600,
                        'pool_timeout': 30,
                        'echo': False
                    }
            
            # 配置连接池参数
            self._engine = create_engine(
                connection_string,
                poolclass=QueuePool,
                **pool_config
            )
            
            logger.info("✅ 数据库连接池初始化成功")
            logger.info(f"📊 连接池配置: {pool_config}")
            
        except Exception as e:
            logger.error(f"❌ 数据库连接池初始化失败: {e}")
            raise
    
    def get_engine(self):
        """获取数据库引擎"""
        if self._engine is None:
            self._create_engine()
        return self._engine
    
    @contextmanager
    def get_connection(self):
        """获取数据库连接的上下文管理器"""
        engine = self.get_engine()
        connection = None
        try:
            connection = engine.connect()
            yield connection
        except Exception as e:
            if connection:
                connection.rollback()
            logger.error(f"❌ 数据库连接操作失败: {e}")
            raise
        finally:
            if connection:
                connection.close()
    
    @contextmanager
    def get_transaction(self):
        """获取数据库事务的上下文管理器"""
        engine = self.get_engine()
        connection = None
        transaction = None
        try:
            connection = engine.connect()
            transaction = connection.begin()
            yield connection
            transaction.commit()
        except Exception as e:
            if transaction:
                transaction.rollback()
            logger.error(f"❌ 数据库事务操作失败: {e}")
            raise
        finally:
            if connection:
                connection.close()
    
    def get_pool_status(self):
        """获取连接池状态信息"""
        if self._engine and hasattr(self._engine.pool, 'status'):
            pool = self._engine.pool
            return {
                'pool_size': pool.size(),
                'checked_in': pool.checkedin(),
                'checked_out': pool.checkedout(),
                'overflow': pool.overflow(),
                'invalid': pool.invalid()
            }
        return None
    
    def close_all_connections(self):
        """关闭所有连接"""
        if self._engine:
            self._engine.dispose()
            logger.info("🔒 数据库连接池已关闭")

# 全局连接池实例
db_pool = DatabaseConnectionPool()

# 便捷函数
def get_db_engine():
    """获取数据库引擎"""
    return db_pool.get_engine()

def get_db_connection():
    """获取数据库连接上下文管理器"""
    return db_pool.get_connection()

def get_db_transaction():
    """获取数据库事务上下文管理器"""
    return db_pool.get_transaction()

def get_pool_status():
    """获取连接池状态"""
    return db_pool.get_pool_status()
import psycopg2
import psycopg2.pool
import logging
from contextlib import contextmanager
from typing import Optional, Dict, Any, List
from config import config

logger = logging.getLogger(__name__)

class DatabaseManager:
    """数据库连接管理器"""
    
    def __init__(self):
        self.stock_pool: Optional[psycopg2.pool.ThreadedConnectionPool] = None
        self.fund_pool: Optional[psycopg2.pool.ThreadedConnectionPool] = None
        self._initialize_pools()
    
    def _initialize_pools(self):
        """初始化连接池"""
        try:
            # 股票数据库连接池
            stock_config = config.get_stock_db_config()
            self.stock_pool = psycopg2.pool.ThreadedConnectionPool(
                minconn=1,
                maxconn=10,
                **stock_config
            )
            logger.info("股票数据库连接池初始化成功")
            
            # 基金数据库连接池
            fund_config = config.get_fund_db_config()
            self.fund_pool = psycopg2.pool.ThreadedConnectionPool(
                minconn=1,
                maxconn=10,
                **fund_config
            )
            logger.info("基金数据库连接池初始化成功")
            
        except Exception as e:
            logger.error(f"数据库连接池初始化失败: {str(e)}")
            raise
    
    @contextmanager
    def get_stock_connection(self):
        """获取股票数据库连接"""
        conn = None
        try:
            conn = self.stock_pool.getconn()
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"股票数据库操作失败: {str(e)}")
            raise
        finally:
            if conn:
                self.stock_pool.putconn(conn)
    
    @contextmanager
    def get_fund_connection(self):
        """获取基金数据库连接"""
        conn = None
        try:
            conn = self.fund_pool.getconn()
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"基金数据库操作失败: {str(e)}")
            raise
        finally:
            if conn:
                self.fund_pool.putconn(conn)
    
    def close_pools(self):
        """关闭连接池"""
        if self.stock_pool:
            self.stock_pool.closeall()
            logger.info("股票数据库连接池已关闭")
        
        if self.fund_pool:
            self.fund_pool.closeall()
            logger.info("基金数据库连接池已关闭")

class QueryBuilder:
    """SQL查询构建器"""
    
    @staticmethod
    def build_stock_query(filters: Dict[str, Any]) -> tuple:
        """构建股票查询SQL"""
        conditions = []
        params = []
        
        # market 筛选（精确匹配）
        if filters.get('market'):
            conditions.append("market = %s")
            params.append(filters['market'])
        
        # symbol 筛选（精确匹配）
        if filters.get('symbol'):
            conditions.append("symbol = %s")
            params.append(filters['symbol'])
        
        # status 筛选（精确匹配）
        status = filters.get('status', 'L')
        conditions.append("status = %s")
        params.append(status)
        
        # name 筛选（模糊匹配）
        if filters.get('name'):
            conditions.append("(cname LIKE %s OR name LIKE %s)")
            like_pattern = filters['name'] + "%"
            params.extend([like_pattern, like_pattern])
        
        # 构建基础SQL
        sql = f"SELECT * FROM {config.STOCK_TABLE}"
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        
        # 排序
        order = filters.get('order', '').lower()
        if order in ('asc', 'desc'):
            sql += f" ORDER BY update_time {order.upper()}"
        else:
            sql += " ORDER BY symbol ASC"
        
        # 限制
        limit = min(filters.get('limit', config.DEFAULT_LIMIT), config.MAX_LIMIT)
        sql += " LIMIT %s"
        params.append(limit)
        
        return sql, params
    
    @staticmethod
    def build_fund_query(filters: Dict[str, Any]) -> tuple:
        """构建基金查询SQL"""
        conditions = []
        params = []
        
        # name 筛选（模糊匹配）
        if filters.get('name'):
            conditions.append("fund_name LIKE %s")
            like_pattern = filters['name'] + "%"
            params.append(like_pattern)
        
        # fund_type 筛选（精确匹配）
        if filters.get('type'):
            conditions.append("fund_type = %s")
            params.append(filters['type'])
        
        # fund_code 筛选（精确匹配）
        if filters.get('code'):
            conditions.append("fund_code = %s")
            params.append(filters['code'])
        
        # status 筛选（精确匹配）
        status = filters.get('status', 'L')
        conditions.append("status = %s")
        params.append(status)
        
        # 构建基础SQL
        sql = f"SELECT * FROM {config.FUND_TABLE}"
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        
        # 排序
        order = filters.get('order', '').lower()
        if order in ('asc', 'desc'):
            sql += f" ORDER BY update_time {order.upper()}"
        else:
            sql += " ORDER BY fund_code ASC"
        
        # 限制
        limit = min(filters.get('limit', config.DEFAULT_LIMIT), config.MAX_LIMIT)
        sql += " LIMIT %s"
        params.append(limit)
        
        return sql, params

def execute_query(sql: str, params: List[Any], db_type: str = 'stock') -> List[Dict[str, Any]]:
    """执行查询并返回结果"""
    db_manager = get_db_manager()
    
    if db_type == 'stock':
        with db_manager.get_stock_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                colnames = [desc[0] for desc in cur.description]
                rows = cur.fetchall()
                return [dict(zip(colnames, row)) for row in rows]
    else:
        with db_manager.get_fund_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                colnames = [desc[0] for desc in cur.description]
                rows = cur.fetchall()
                return [dict(zip(colnames, row)) for row in rows]

# 全局数据库管理器实例（延迟初始化）
db_manager = None

def get_db_manager():
    """获取数据库管理器实例（延迟初始化）"""
    global db_manager
    if db_manager is None:
        db_manager = DatabaseManager()
    return db_manager
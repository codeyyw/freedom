import logging
import os
import time

import akshare as ak
from sqlalchemy import create_engine, text

# 导入连接池管理器
from common.db_pool import get_db_engine, get_db_connection, get_db_transaction

from .data_processor import FundDataProcessor
from .db_operations import FundDatabase
from common.config import FUND_CONFIG as DB_CONFIG

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s %(threadName)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def get_engine():
    """获取数据库连接引擎（优先使用连接池）"""
    if get_db_engine is not None:
        # 使用连接池管理器
        return get_db_engine()
    else:
        # 降级到原有方式
        return _create_legacy_engine()

def _create_legacy_engine():
    """创建传统数据库引擎（备用方案）"""
    user = os.environ.get("PG_USER")
    password = os.environ.get("PG_PASSWORD")
    host = os.environ.get("PG_HOST_OUT") or os.environ.get("PG_HOST")    
    port = os.environ.get("PG_PORT", "5432")
    dbname = os.environ.get("PG_DB")
    
    if not all([user, password, host, dbname]):
        logger.error("缺少必要的环境变量，请检查PG_USER, PG_PASSWORD, PG_HOST_OUT, PG_DB")
        return None
        
    conn_str = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}"
    engine = create_engine(conn_str, echo=False, future=True)
    return engine   

def sync_task_runner():
    """主函数：执行基金数据同步"""
    start_time = time.time()
    
    # 初始化数据库连接和处理器
    engine = get_engine()
    if engine is None:
        logger.error("数据库连接失败，程序退出")
        return
    
    # 使用配置文件中的参数初始化数据库操作类
    db = FundDatabase(
        engine, 
        max_workers=DB_CONFIG["max_workers"], 
        batch_size=DB_CONFIG["batch_size"]
    )
    processor = FundDataProcessor()
    
    logger.info(f"🔧 系统配置:")
    logger.info(f"   - 数据接口调用: 串行执行（避免API限制）")
    logger.info(f"   - 数据库操作: {DB_CONFIG['max_workers']} 线程并发")
    logger.info(f"   - 批次大小: {DB_CONFIG['batch_size']} 条/批")
    logger.info(f"   - 重试次数: {DB_CONFIG['max_retry']} 次")
    logger.info(f"   - 重试延迟: {DB_CONFIG['retry_delay']} 秒")
    logger.info("开始基金数据同步任务")
    
    # 第一步：收集所有基金数据
    fund_data = processor.collect_all_fund_data()
    if not fund_data:
        logger.error("❌ 基金数据获取不完整，任务终止，不会与数据库交互")
        logger.error("请检查网络连接和API接口状态，确保所有五个数据源都能正常访问")
        return
    
    logger.info(f"✅ 所有基金数据获取成功，共 {len(fund_data)} 个类型")
    
    # 第二步：整合基金数据，处理重复编码
    final_funds, _ = processor.integrate_fund_data(fund_data)
    
    # 第三步：获取数据库现有数据并分析差异
    existing_codes = db.get_existing_fund_codes()
    new_codes, removed_codes, update_codes = processor.analyze_data_differences(final_funds, existing_codes)
    
    # 第四步：执行数据库更新操作
    logger.info("开始执行数据库更新操作...")
    db.execute_batch_updates(final_funds, new_codes, removed_codes, update_codes)
    
    total_time = time.time() - start_time
    logger.info(f"基金数据同步任务完成，总耗时: {total_time:.4f} 秒")

if __name__ == "__main__":
    sync_task_runner()



def handler(event, context):
    logger.warning("收到调用请求，开始同步执行批量更新任务...")
    sync_task_runner()
    logger.warning("同步任务完成，准备返回。")
    return "批量更新任务执行完毕，日志已完整输出"
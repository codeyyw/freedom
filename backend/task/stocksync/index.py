import logging
import time
from typing import Set

import akshare as ak
from common.db_pool import get_db_engine

from .db_operations import get_existing_stock_symbols_by_market, update_stock_records_batch, insert_stock_records_batch, mark_stocks_as_deleted
from .data_processor import StockDataProcessor

# 直接导入配置，如果配置文件不存在则报错
from common.config import LOG_CONFIG, STOCK_CONFIG as DB_CONFIG, MARKET_CONFIGS, RETRY_CONFIG

logging.basicConfig(
    level=getattr(logging, LOG_CONFIG["level"]),
    format=LOG_CONFIG["format"],
    datefmt=LOG_CONFIG["datefmt"]
)
logger = logging.getLogger(__name__)


def sync_task_runner():
    """股票数据同步任务主函数"""
    start_time = time.time()
    
    logger.info("🚀 股票数据同步系统启动")
    logger.info("📅 开始执行股票数据同步任务")
    
    try:
        # 初始化股票数据处理器
        processor = StockDataProcessor()
        
        # 初始化数据库连接
        logger.info("🔗 正在连接数据库...")
        engine = get_db_engine()
        existing_symbols_map = get_existing_stock_symbols_by_market(engine)
        logger.info("✅ 数据库连接成功")
        
        # 收集所有市场数据
        result = processor.collect_all_stock_data(existing_symbols_map)

        # 任务完成统计
        logger.info("🎉 股票数据同步任务完成！")
        logger.info(f"📊 处理统计: 已处理 {result['processed']} 个市场, 跳过 {result['skipped']} 个市场")
        
        return {'success': True, 'result': result}
        
    except Exception as e:
        logger.error("❌ 任务运行异常", exc_info=True)
        return {'success': False, 'error': str(e)}
    finally:
        total_duration = time.time() - start_time
        # 创建临时处理器实例来使用format_duration方法
        temp_processor = StockDataProcessor()
        logger.info(f"⏱️  总耗时: {temp_processor.format_duration(total_duration)}")


def handler(event, context):
    logger.warning("收到调用请求，开始同步执行批量更新任务...")
    sync_task_runner()
    logger.warning("同步任务完成，准备返回。")
    return "批量更新任务执行完毕，日志已完整输出"

if __name__ == "__main__":
    sync_task_runner()

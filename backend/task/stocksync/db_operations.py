import logging
import traceback
import threading
import time
from sqlalchemy import text

# 导入统一的SQL管理
from common import StockSQL

logger = logging.getLogger(__name__)

# 使用统一的SQL定义
UPDATE_SQL = StockSQL.UPDATE_STOCK
INSERT_SQL = StockSQL.INSERT_STOCK
MARK_DELETE_SQL = StockSQL.MARK_STOCKS_DELETED
GET_EXISTING_SYMBOLS_SQL = StockSQL.GET_EXISTING_SYMBOLS


def get_existing_stock_symbols_by_market(engine):
    """获取数据库中已存在的股票symbol列表，按市场分类"""
    logger.info("📊 开始查询数据库中的已存在股票symbol列表")
    symbol_map = {}
    try:
        with engine.connect() as conn:
            result = conn.execute(GET_EXISTING_SYMBOLS_SQL)
            count = 0
            for row in result:
                try:
                    market = row._mapping['market']
                    symbol = row._mapping['symbol']
                except AttributeError:
                    market = row[1]
                    symbol = row[0]
                symbol_map.setdefault(market, set()).add(symbol)
                count += 1
        
        # 统计信息
        market_stats = {m: len(s) for m, s in symbol_map.items()}
        logger.info(f"✅ 查询完成，数据库股票总记录数：{count}")
        logger.info(f"📈 市场分类统计：{market_stats}")
        return symbol_map
    except Exception as e:
        logger.error(f"❌ 查询数据库股票symbol列表异常: {e}")
        logger.error(traceback.format_exc())
        return symbol_map


def update_stock_records_batch(engine, batch_records, batch_num, market_name, failed_symbols):
    """批量更新股票记录（优化版本）"""
    threadbare = threading.current_thread().name
    logger.info(f"🔄 [{market_name}][{threadbare}] 更新批次 {batch_num}: 准备更新 {len(batch_records)} 条记录")
    
    symbols_in_batch = [rec.get('symbol', '') for rec in batch_records]
    if len(symbols_in_batch) <= 20:
        logger.info(f"📝 [{market_name}][{threadbare}] 批次 {batch_num} 包含symbols: {symbols_in_batch}")
    else:
        logger.info(f"📝 [{market_name}][{threadbare}] 批次 {batch_num} 包含symbols（前20个）: {symbols_in_batch[:20]}")

    start_time = time.time()
    try:
        with engine.begin() as conn:
            # 使用executemany进行批量更新，提升性能
            batch_data = []
            for record in batch_records:
                record['market'] = market_name
                batch_data.append(record)
            
            try:
                # 批量执行更新
                result = conn.execute(UPDATE_SQL, batch_data)
                # 检查是否有记录未被更新
                for i, record in enumerate(batch_data):
                    if i < len(batch_data) and not hasattr(result, 'rowcount') or result.rowcount == 0:
                        failed_symbols.append(record['symbol'])
                        logger.warning(f"⚠️ [{market_name}][{threadbare}] 更新未影响行，symbol={record['symbol']}")
            except Exception as e:
                # 如果批量更新失败，回退到逐条更新
                logger.warning(f"⚠️ [{market_name}][{threadbare}] 批量更新失败，回退到逐条更新: {e}")
                for record in batch_data:
                    try:
                        res = conn.execute(UPDATE_SQL, record)
                        if res.rowcount == 0:
                            failed_symbols.append(record['symbol'])
                            logger.warning(f"⚠️ [{market_name}][{threadbare}] 更新未影响行，symbol={record['symbol']}")
                    except Exception as e:
                        logger.error(f"❌ [{market_name}][{threadbare}] 批次 {batch_num} 更新失败，symbol={record.get('symbol')}, 错误: {e}")
                        failed_symbols.append(record.get('symbol'))
        duration = time.time() - start_time
        logger.info(f"✅ [{market_name}][{threadbare}] 更新批次 {batch_num} 完成，耗时 {duration:.4f} 秒")
        return len(batch_records), duration, None
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"[{market_name}][{threadbare}] 更新批次 {batch_num} 事务失败，错误: {e}，耗时 {duration:.4f} 秒")
        logger.error(traceback.format_exc())
        return 0, duration, e


def insert_stock_records_batch(engine, batch_records, batch_num, market_name):
    """批量插入新股票记录（优化版本）"""
    threadname = threading.current_thread().name
    logger.info(f"➕ [{market_name}][{threadname}] 插入批次 {batch_num}: 准备插入 {len(batch_records)} 条记录")
    
    symbols_in_batch = [rec.get('symbol', '') for rec in batch_records]
    if len(symbols_in_batch) <= 20:
        logger.info(f"📝 [{market_name}][{threadname}] 批次 {batch_num} 包含symbols: {symbols_in_batch}")
    else:
        logger.info(f"📝 [{market_name}][{threadname}] 批次 {batch_num} 包含symbols（前20个）: {symbols_in_batch[:20]}")

    start_time = time.time()
    try:
        with engine.begin() as conn:
            # 准备批量插入数据
            batch_data = []
            for record in batch_records:
                record['market'] = market_name
                batch_data.append(record)
            
            try:
                # 使用executemany进行批量插入，提升性能
                conn.execute(INSERT_SQL, batch_data)
            except Exception as e:
                # 如果批量插入失败，回退到逐条插入
                logger.warning(f"⚠️ [{market_name}][{threadname}] 批量插入失败，回退到逐条插入: {e}")
                for record in batch_data:
                    try:
                        conn.execute(INSERT_SQL, record)
                    except Exception as e:
                        logger.error(f"❌ [{market_name}][{threadname}] 批次 {batch_num} 插入失败，symbol={record.get('symbol')}, 错误: {e}")
        
        duration = time.time() - start_time
        logger.info(f"✅ [{market_name}][{threadname}] 插入批次 {batch_num} 完成，耗时 {duration:.4f} 秒")
        return len(batch_records), duration, None
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"❌ [{market_name}][{threadname}] 插入批次 {batch_num} 事务失败，错误: {e}，耗时 {duration:.4f} 秒")
        logger.error(traceback.format_exc())
        return 0, duration, e


def mark_stocks_as_deleted(engine, symbols_to_delete, market_name):
    """标记股票为删除状态"""
    threadbare = threading.current_thread().name
    if not symbols_to_delete:
        logger.info(f"✅ [{market_name}][{threadbare}] 无需标记删除的股票")
        return 0
    
    if len(symbols_to_delete) <= 20:
        logger.info(f"📝 [{market_name}][{threadbare}] 标记删除股票symbols: {list(symbols_to_delete)}")
    else:
        logger.info(f"📝 [{market_name}][{threadbare}] 标记删除股票symbols（前20个）: {list(symbols_to_delete)[:20]}")
    logger.info(f"🗑️ [{market_name}][{threadbare}] 标记删除股票数量：{len(symbols_to_delete)}")
    
    try:
        start_time = time.time()
        with engine.begin() as conn:
            res = conn.execute(MARK_DELETE_SQL, {"symbols": list(symbols_to_delete), "market": market_name})
            count = res.rowcount
        duration = time.time() - start_time
        logger.info(f"✅ [{market_name}][{threadbare}] 标记删除完成，受影响行数：{count}，耗时 {duration:.4f} 秒")
        return count
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"❌ [{market_name}][{threadbare}] 标记删除失败，错误: {e}，耗时 {duration:.4f} 秒")
        logger.error(traceback.format_exc())
        return 0

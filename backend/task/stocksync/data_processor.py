#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票数据处理模块
"""

import logging
import os
import time
from typing import Dict, List, Set, Tuple, Optional, Any

import akshare as ak
import pandas as pd
from sqlalchemy import create_engine

# 导入抽象基类和工厂模式
from common.base_processor import BaseDataProcessor
from common.data_factory import create_data_factory, StockDataFactory

# 导入连接池管理器
from common.db_pool import get_db_engine, get_db_connection, get_db_transaction

# 导入数据库操作模块
from .db_operations import (
    get_existing_stock_symbols_by_market,
    update_stock_records_batch,
    insert_stock_records_batch,
    mark_stocks_as_deleted,
)

# 导入市场状态检查模块
from .market_status import is_us_stock_market_open, check_market_open_status, is_hk_stock_market_open, is_a_stock_market_open

# 导入股票清洗模块
from .stock_cleaners import clean_a_stock_data, clean_hk_stock_data, clean_us_stock_data

# 导入配置
from common.config import STOCK_CONFIG as DB_CONFIG, RETRY_CONFIG

logger = logging.getLogger(__name__)

class StockDataProcessor(BaseDataProcessor):
    """股票数据处理器"""
    
    def __init__(self):
        """初始化股票数据处理器"""
        super().__init__()
        
        self.log_section_start("🔧 开始初始化股票数据处理器")
        
        # 初始化数据工厂（必须成功）
        try:
            self.data_factory = create_data_factory("stock")
            if not self.data_factory:
                raise RuntimeError("数据工厂创建失败")
            logger.info("✅ 数据工厂初始化成功")
        except Exception as e:
            logger.error(f"❌ 数据工厂初始化失败: {e}")
            raise RuntimeError(f"数据工厂初始化失败: {e}")
        
        # 使用工厂模式配置
        self.market_configs = self._create_market_configs_from_factory()
        logger.info("✅ 使用工厂模式配置")
        
        logger.info("-" * 40)
        logger.info(f"🎯 股票数据处理器初始化完成")
        logger.info(f"📊 成功配置: {len(self.market_configs)} 个市场")
        
        if self.market_configs:
            logger.info("✅ 已配置的市场:")
            for config in self.market_configs:
                market_name = config["market_name"]
                func_name = config["get_data_func"].__name__
                concurrency = config["concurrency"]
                logger.info(f"   - {market_name}: {func_name} (并发数: {concurrency})")
        else:
            logger.error("❌ 没有成功配置任何市场！")
            
        self.log_section_end("股票数据处理器初始化完成")
    
    def _create_market_configs_from_factory(self) -> List[Dict[str, Any]]:
        """从工厂创建市场配置"""
        configs = []
        
        # 市场开盘检查函数映射
        check_open_funcs = {
            "A股": is_a_stock_market_open,
            "港股": is_hk_stock_market_open,
            "美股": is_us_stock_market_open
        }
        
        for source_config in self.data_factory.get_all_data_sources():
            config = {
                "market_name": source_config.name,
                "get_data_func": source_config.api_func,
                "clean_func": source_config.clean_func,
                "check_open_func": check_open_funcs.get(source_config.name),
                "concurrency": source_config.concurrency,
            }
            configs.append(config)
        
        return configs
    
    def get_data_sources(self) -> List[Dict[str, Any]]:
        """获取数据源配置"""
        return self.market_configs
    
    def safe_get_data(self, get_func, source_name: str, **kwargs) -> Optional[Any]:
        """安全获取数据"""
        try:
            if get_func is None:
                logger.warning(f"数据源 {source_name} 的获取函数为空")
                return None
                
            # 调用数据获取函数
            data = get_func(**kwargs)
            
            if data is None or (hasattr(data, 'empty') and data.empty):
                logger.warning(f"数据源 {source_name} 返回空数据")
                return None
                
            logger.info(f"成功获取 {source_name} 数据，记录数: {len(data) if hasattr(data, '__len__') else '未知'}")
            return data
            
        except Exception as e:
            logger.error(f"获取 {source_name} 数据失败: {str(e)}")
            return None
    
    def process_data(self, data: pd.DataFrame, market_name: str) -> pd.DataFrame:
        """处理数据"""
        # 找到对应市场的清洗函数
        for config in self.market_configs:
            if config["market_name"] == market_name:
                clean_func = config["clean_func"]
                return clean_func(data)
        
        raise ValueError(f"未找到市场 {market_name} 的清洗函数")
    
    def sync_to_database(self, data: pd.DataFrame, market_name: str, db_connection) -> Dict[str, Any]:
        """同步数据到数据库"""
        return self.process_market_records(data, market_name, db_connection)
    
    def safely_get_market_data(self, get_data_func, market_name: str, max_retry: int = None):
        """安全获取市场数据，带增强的重试机制和错误分类"""
        if max_retry is None:
            max_retry = RETRY_CONFIG.get("max_retry", 3)
        
        retry_delay = RETRY_CONFIG.get("retry_delay", 2)
        timeout = RETRY_CONFIG.get("timeout", 30)
        
        for attempt in range(max_retry):
            try:
                logger.info(f"🔄 [{market_name}] 第 {attempt + 1}/{max_retry} 次尝试获取数据")
                
                # 设置超时
                import signal
                signal.alarm(timeout)
                
                data = get_data_func()
                
                # 取消超时
                signal.alarm(0)
                
                # 数据验证
                if data is None or len(data) == 0:
                    raise ValueError(f"获取到空数据或无效数据")
                
                logger.info(f"✅ [{market_name}] 数据获取成功，共 {len(data)} 条记录")
                return data
                
            except Exception as e:
                signal.alarm(0)  # 确保取消超时
                
                # 错误分类处理
                error_type = self._classify_error(e)
                logger.error(f"❌ [{market_name}] 第 {attempt + 1} 次获取数据失败 [{error_type}]: {e}")
                
                # 根据错误类型决定是否重试
                if not self._should_retry(error_type, attempt, max_retry):
                    logger.error(f"💥 [{market_name}] 错误类型 {error_type} 不适合重试，直接失败")
                    return None
                
                if attempt < max_retry - 1:
                    # 根据错误类型调整重试延迟
                    adjusted_delay = self._get_retry_delay(error_type, retry_delay, attempt)
                    logger.info(f"⏳ [{market_name}] {adjusted_delay} 秒后重试...")
                    time.sleep(adjusted_delay)
                else:
                    logger.error(f"💥 [{market_name}] 所有重试均失败，放弃获取数据")
        
        return None
    
    # 错误处理方法已移至基类 BaseDataProcessor
    
    def format_duration(self, duration_sec: float) -> str:
        """格式化时间显示"""
        if duration_sec >= 120:
            return f"{duration_sec / 60:.4f} 分钟"
        else:
            return f"{duration_sec:.4f} 秒"
    
    def process_and_sync_stock_data(
        self,
        market_name: str,
        get_data_func,
        clean_func,
        existing_symbols: Set[str],
        concurrency: int = 2,
        batch_size: int = None,
    ):
        """处理并同步股票数据"""
        if batch_size is None:
            batch_size = DB_CONFIG["batch_size"]
        
        self.log_section_start(f"🚀 开始处理 [{market_name}] 股票数据")
        logger.info(f"📊 已存在股票数量: {len(existing_symbols)}")
        
        start_time = time.time()

        # 获取原始数据
        raw_dataframe = self.safely_get_market_data(get_data_func, market_name)
        if raw_dataframe is None or raw_dataframe.empty:
            logger.error(f"❌ [{market_name}] 拉取到的数据为空，跳过本次市场处理！")
            self.log_section_end(f"[{market_name}] 处理结束")
            return

        logger.info(f"📥 [{market_name}] 原始数据行数: {len(raw_dataframe)}")
        
        # 清洗数据
        cleaned_dataframe = clean_func(raw_dataframe)
        cleaned_dataframe = cleaned_dataframe.dropna(subset=["symbol", "datetime"])
        logger.info(f"🧹 [{market_name}] 清洗后数据行数: {len(cleaned_dataframe)}")
        
        # 内存优化：释放原始数据
        del raw_dataframe
        
        # 内存优化：分块处理大数据集
        chunk_size = 10000  # 每次处理10000条记录
        total_rows = len(cleaned_dataframe)
        
        if total_rows > chunk_size:
            logger.info(f"📦 [{market_name}] 大数据集检测，启用分块处理模式 (chunk_size={chunk_size})")
            
            exist_records = []
            new_records = []
            new_symbols = set()
            
            # 分块处理
            for i in range(0, total_rows, chunk_size):
                chunk_end = min(i + chunk_size, total_rows)
                chunk_df = cleaned_dataframe.iloc[i:chunk_end]
                
                logger.info(f"📦 [{market_name}] 处理数据块 {i//chunk_size + 1}/{(total_rows-1)//chunk_size + 1} ({i+1}-{chunk_end})")
                
                chunk_records = chunk_df.to_dict(orient="records")
                chunk_symbols = set(chunk_df["symbol"].unique())
                new_symbols.update(chunk_symbols)
                
                # 分类记录
                chunk_exist = [r for r in chunk_records if r["symbol"] in existing_symbols]
                chunk_new = [r for r in chunk_records if r["symbol"] not in existing_symbols]
                
                exist_records.extend(chunk_exist)
                new_records.extend(chunk_new)
                
                # 清理临时变量
                del chunk_df, chunk_records, chunk_symbols, chunk_exist, chunk_new
        else:
            # 小数据集直接处理
            records = cleaned_dataframe.to_dict(orient="records")
            new_symbols = set(cleaned_dataframe["symbol"].unique())
            
            # 分类记录
            exist_records = [r for r in records if r["symbol"] in existing_symbols]
            new_records = [r for r in records if r["symbol"] not in existing_symbols]
            
            # 清理临时变量
            del records
        
        # 清理DataFrame
        del cleaned_dataframe
        
        removed_symbols = existing_symbols - new_symbols

        logger.info("-" * 40)
        logger.info(f"📈 [{market_name}] 数据统计")
        logger.info(f"🆕 新增记录: {len(new_records)} 条")
        logger.info(f"🔄 更新记录: {len(exist_records)} 条")
        logger.info(f"🗑️  删除记录: {len(removed_symbols)} 条")
        logger.info("-" * 40)

        # 处理数据库操作
        engine = self.get_db_engine()

        result = self.process_market_records(
            engine,
            market_name,
            exist_records,
            new_records,
            removed_symbols,
            batch_size=batch_size,
            concurrency=concurrency,
        )

        duration = time.time() - start_time
        logger.info("-" * 40)
        logger.info(f"🎉 [{market_name}] 处理完成！")
        logger.info(f"⏱️  总耗时: {self.format_duration(duration)}")
        logger.info(f"📊 处理结果: 更新 {result['updated']} 条, 新增 {result['inserted']} 条, 删除 {result['deleted']} 条")
        
        failed_updates = result.get("failed_updates") or []
        if failed_updates:
            logger.warning(f"⚠️  更新失败: {len(failed_updates)} 条")
            logger.warning(f"[{market_name}] 更新失败股票：{sorted(set(failed_updates))}")
        logger.info("-" * 40)
    
    def collect_all_stock_data(self, existing_symbols_map: Dict[str, Set[str]]) -> Dict[str, int]:
        """收集所有市场的股票数据"""
        logger.info("-" * 50)
        logger.info(f"📋 准备处理 {len(self.market_configs)} 个市场")
        logger.info("-" * 50)

        processed_markets = 0
        skipped_markets = 0
        
        for conf in self.market_configs:
            market_name = conf["market_name"]
            if check_market_open_status(conf["check_open_func"], 2):
                logger.info(f"🟢 [{market_name}] 当前或两小时前为开盘时间，开始处理...")
                existing_symbols = existing_symbols_map.get(market_name, set())
                self.process_and_sync_stock_data(
                    market_name,
                    conf["get_data_func"],
                    conf["clean_func"],
                    existing_symbols,
                    concurrency=conf["concurrency"],
                )
                processed_markets += 1
            else:
                logger.info(f"🔴 [{market_name}] 当前及两小时前均非开盘时间，跳过处理")
                skipped_markets += 1
        
        return {
            "processed": processed_markets,
            "skipped": skipped_markets
        }
    
    def get_db_engine(self):
        """获取数据库引擎（优先使用连接池）"""
        if get_db_engine is not None:
            # 使用连接池管理器
            return get_db_engine()
        else:
            # 降级到原有方式
            return self._create_legacy_engine()
    
    def _create_legacy_engine(self):
        """创建传统数据库引擎（备用方案）"""
        user = os.environ.get("PG_USER")
        password = os.environ.get("PG_PASSWORD")
        host = os.environ.get("PG_HOST")
        port = os.environ.get("PG_PORT", "5432")
        dbname = os.environ.get("PG_DB")
        conn_str = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}"
        logger.info(f"构造数据库连接字符串成功: user={user}, host={host}, port={port}, dbname={dbname}")
        # 使用统一的连接池管理
        return get_db_engine()
    
    def process_market_records(
        self,
        engine,
        market_name: str,
        exist_records,
        new_records,
        removed_symbols,
        batch_size=1500,
        concurrency=2,
    ):
        """处理市场记录的批量操作"""
        from concurrent.futures import ThreadPoolExecutor, as_completed

        failed_update_symbols = []

        total_updated = 0
        total_update_duration = 0.0
        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = [
                executor.submit(update_stock_records_batch, engine, exist_records[i:i+batch_size], idx+1, market_name, failed_update_symbols)
                for idx, i in enumerate(range(0, len(exist_records), batch_size))
            ]
            for future in as_completed(futures):
                updated, duration, error = future.result()
                if error is None:
                    total_updated += updated
                    total_update_duration += duration

        logger.info(f"[{market_name}] 批量更新完成，更新条数：{total_updated}，任务总耗时：{self.format_duration(total_update_duration)}")

        total_inserted = 0
        total_insert_duration = 0.0
        if new_records:
            with ThreadPoolExecutor(max_workers=concurrency) as executor:
                futures = [
                    executor.submit(insert_stock_records_batch, engine, new_records[i:i+batch_size], idx+1, market_name)
                    for idx, i in enumerate(range(0, len(new_records), batch_size))
                ]
                for future in as_completed(futures):
                    inserted, duration, error = future.result()
                    if error is None:
                        total_inserted += inserted
                        total_insert_duration += duration
            logger.info(f"[{market_name}] 批量插入完成，插入条数：{total_inserted}，任务总耗时：{self.format_duration(total_insert_duration)}")
        else:
            logger.info(f"[{market_name}] 无新增股票插入")

        deleted_count = 0
        del_duration = 0.0
        if removed_symbols:
            deleted_count, del_duration = mark_stocks_as_deleted(engine, removed_symbols, market_name)
        else:
            logger.info(f"[{market_name}] 无需标记删除股票")

        return {
            "updated": total_updated,
            "update_time": total_update_duration,
            "inserted": total_inserted,
            "insert_time": total_insert_duration,
            "deleted": deleted_count,
            "delete_time": del_duration,
            "failed_updates": failed_update_symbols,
        }
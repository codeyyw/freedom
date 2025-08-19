#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库操作模块
"""

import logging
import time
from datetime import datetime
from typing import List, Set, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

from sqlalchemy import create_engine, text
from psycopg2.extras import execute_values

# 导入统一的SQL管理
from common import FundSQL

logger = logging.getLogger(__name__)

class FundDatabase:
    """基金数据库操作类"""
    
    def __init__(self, engine, max_workers=4, batch_size=1000):
        self.engine = engine
        self.max_workers = max_workers
        self.batch_size = batch_size
    
    def get_existing_fund_codes(self) -> Set[str]:
        """获取数据库中现有的基金编码"""
        with self.engine.connect() as conn:
            res = conn.execute(FundSQL.GET_EXISTING_FUND_CODES)
            return {row[0] for row in res.fetchall()}
    
    def mark_funds_deleted(self, fund_codes: Set[str]) -> float:
        """标记基金为删除状态"""
        if not fund_codes:
            return 0.0
            
        start_time = time.time()
        logger.info(f"开始标记 {len(fund_codes)} 个基金为删除状态")
        
        with self.engine.connect() as conn:
            with conn.begin():
                conn.execute(FundSQL.MARK_FUNDS_DELETED, {"codes": list(fund_codes)})
        
        duration = time.time() - start_time
        logger.info(f"标记删除完成，耗时: {duration:.4f} 秒")
        return duration
    
    def _batch_insert_worker(self, batch_data: List[Tuple], worker_id: int) -> float:
        """单个线程的批量插入操作 - 优化版本"""
        start_time = time.time()
        
        # 准备插入数据
        insert_data = [
            (code, name, fund_type, price, 'L') 
            for code, name, fund_type, price in batch_data
        ]
        
        try:
            with self.engine.connect() as conn:
                with conn.begin():
                    with conn.connection.cursor() as cursor:
                        execute_values(cursor, FundSQL.INSERT_FUNDS_BATCH, insert_data, template="(%s,%s,%s,%s,%s)")
            
            duration = time.time() - start_time
            logger.info(f"[线程-{worker_id}] 批量插入 {len(batch_data)} 条记录，耗时: {duration:.4f} 秒")
            return duration
        except Exception as e:
            logger.error(f"[线程-{worker_id}] 批量插入失败: {e}")
            raise
    
    def _batch_update_worker(self, batch_data: List[Tuple], worker_id: int) -> float:
        """单个线程的批量更新操作 - 优化版本"""
        start_time = time.time()
        
        try:
            with self.engine.connect() as conn:
                with conn.begin():
                    with conn.connection.cursor() as cursor:
                        # 准备批量更新数据
                        update_data = [
                            (code, name, price) 
                            for code, name, _, price in batch_data
                        ]
                        
                        # 使用execute_values执行批量更新
                        execute_values(cursor, FundSQL.UPDATE_FUNDS_BATCH, update_data, template="(%s,%s,%s)")
            
            duration = time.time() - start_time
            logger.info(f"[线程-{worker_id}] 批量更新 {len(batch_data)} 条记录，耗时: {duration:.4f} 秒")
            return duration
        except Exception as e:
            logger.error(f"[线程-{worker_id}] 批量更新失败: {e}")
            raise
    
    def insert_new_funds(self, funds: List[Tuple]) -> float:
        """多线程批量插入新基金"""
        if not funds:
            return 0.0
            
        start_time = time.time()
        logger.info(f"开始多线程插入 {len(funds)} 个新基金，线程数: {self.max_workers}")
        
        # 分批处理
        batches = [funds[i:i + self.batch_size] for i in range(0, len(funds), self.batch_size)]
        logger.info(f"数据分为 {len(batches)} 个批次，每批最大 {self.batch_size} 条")
        
        total_duration = 0.0
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有批次任务
            future_to_batch = {
                executor.submit(self._batch_insert_worker, batch, i): i 
                for i, batch in enumerate(batches)
            }
            
            # 等待所有任务完成
            for future in as_completed(future_to_batch):
                batch_id = future_to_batch[future]
                try:
                    duration = future.result()
                    total_duration += duration
                except Exception as e:
                    logger.error(f"批次 {batch_id} 执行失败: {e}")
                    raise
        
        duration = time.time() - start_time
        logger.info(f"多线程插入完成，总耗时: {duration:.4f} 秒，实际插入耗时: {total_duration:.4f} 秒")
        return duration
    
    def update_existing_funds(self, funds: List[Tuple]) -> float:
        """多线程批量更新现有基金"""
        if not funds:
            return 0.0
            
        start_time = time.time()
        logger.info(f"开始多线程更新 {len(funds)} 个现有基金，线程数: {self.max_workers}")
        
        # 分批处理
        batches = [funds[i:i + self.batch_size] for i in range(0, len(funds), self.batch_size)]
        logger.info(f"数据分为 {len(batches)} 个批次，每批最大 {self.batch_size} 条")
        
        total_duration = 0.0
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有批次任务
            future_to_batch = {
                executor.submit(self._batch_update_worker, batch, i): i 
                for i, batch in enumerate(batches)
            }
            
            # 等待所有任务完成
            for future in as_completed(future_to_batch):
                batch_id = future_to_batch[future]
                try:
                    duration = future.result()
                    total_duration += duration
                except Exception as e:
                    logger.error(f"批次 {batch_id} 执行失败: {e}")
                    raise
        
        duration = time.time() - start_time
        logger.info(f"多线程更新完成，总耗时: {duration:.4f} 秒，实际更新耗时: {total_duration:.4f} 秒")
        return duration
    
    def execute_batch_updates(self, final_funds: List[Tuple], new_codes: Set[str], removed_codes: Set[str], update_codes: Set[str]) -> float:
        """执行批量数据库更新操作"""
        start_time = time.time()
        
        # 1. 标记删除
        self.mark_funds_deleted(removed_codes)
        
        # 2. 插入新基金
        new_funds = [f for f in final_funds if f[0] in new_codes]
        self.insert_new_funds(new_funds)
        
        # 3. 更新现有基金
        update_funds = [f for f in final_funds if f[0] in update_codes]
        self.update_existing_funds(update_funds)
        
        total_duration = time.time() - start_time
        logger.info(f"数据库更新操作完成，总耗时: {total_duration:.4f} 秒")
        return total_duration
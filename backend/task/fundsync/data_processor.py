#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基金数据处理模块
"""

import logging
import time
from typing import Dict, List, Set, Tuple, Optional, Any

import akshare as ak
import pandas as pd
from requests.exceptions import ChunkedEncodingError

# 导入抽象基类和工厂模式
from common.base_processor import BaseDataProcessor
from common.data_factory import create_data_factory, FundDataFactory

# 导入连接池管理器
from common.db_pool import get_db_engine, get_db_connection, get_db_transaction

# 导入配置
from common.config import FUND_TYPES, FUND_CONFIG as DB_CONFIG

logger = logging.getLogger(__name__)

class FundDataProcessor(BaseDataProcessor):
    """基金数据处理器"""
    
    def __init__(self):
        # 调用父类初始化
        super().__init__()
        
        # 使用工厂模式初始化
        self.data_factory = create_data_factory('fund')
        
        # 动态导入akshare函数
        self.fund_tasks = []
        self.log_section_start("🔧 开始初始化基金数据处理器")
        logger.info("✅ 使用工厂模式配置")
        self.log_section_end("基金数据处理器初始化完成")
        
        for fund_type, config in FUND_TYPES.items():
            try:
                api_func_name = config["api_func"]
                logger.info(f"📋 基金类型 '{fund_type}' 配置: {api_func_name}")
                
                # 直接使用akshare模块的函数
                if hasattr(ak, api_func_name):
                    func = getattr(ak, api_func_name)
                    logger.info(f"✅ 成功获取函数: {api_func_name}")
                    self.fund_tasks.append((fund_type, func, config["concurrency"]))
                else:
                    logger.error(f"❌ 未找到函数: {api_func_name} 在 akshare 模块中")
                    available_funcs = [attr for attr in dir(ak) if not attr.startswith('_')]
                    logger.info(f"💡 可用的 akshare 函数示例: {available_funcs[:10]}...")
                    logger.info(f"💡 总共 {len(available_funcs)} 个可用函数")
            except Exception as e:
                logger.error(f"❌ 初始化基金类型 '{fund_type}' 失败: {e}", exc_info=True)
        
        logger.info("-" * 40)
        logger.info(f"🎯 基金数据处理器初始化完成")
        logger.info(f"📊 成功配置: {len(self.fund_tasks)}/{len(FUND_TYPES)} 个基金类型")
        
        if self.fund_tasks:
            logger.info("✅ 已配置的基金类型:")
            for fund_type, func, concurrency in self.fund_tasks:
                logger.info(f"   - {fund_type}: {func.__name__} (并发数: {concurrency})")
        else:
            logger.error("❌ 没有成功配置任何基金类型！")
            
        logger.info("=" * 60)
    
    def safe_get_data(self, get_func, fund_name: str, max_retry=None) -> Optional:
        """安全获取数据，带增强的重试机制和错误分类"""
        if max_retry is None:
            max_retry = DB_CONFIG["max_retry"]
        
        # 获取函数名称用于日志
        func_name = get_func.__name__ if hasattr(get_func, '__name__') else str(get_func)
        logger.info(f"[{fund_name}] 开始调用函数: {func_name}")
            
        for attempt in range(max_retry):
            try:
                logger.info(f"[{fund_name}] 第 {attempt+1} 次尝试调用 {func_name}")
                df = get_func()
                logger.info(f"[{fund_name}] {func_name} 调用成功，返回数据类型: {type(df)}")
                
                if df is not None and not df.empty:
                    logger.info(f"[{fund_name}] {func_name} 返回数据行数: {len(df)}, 列数: {len(df.columns) if hasattr(df, 'columns') else 'N/A'}")
                    return df
                else:
                    logger.warning(f"[{fund_name}] {func_name} 返回数据为空或None，第 {attempt+1} 次重试")
            except Exception as e:
                # 错误分类处理
                error_type = self._classify_error(e)
                logger.error(f"❌ [{fund_name}] 第 {attempt + 1} 次获取数据失败 [{error_type}]: {e}")
                
                # 根据错误类型决定是否重试
                if not self._should_retry(error_type, attempt, max_retry):
                    logger.error(f"💥 [{fund_name}] 错误类型 {error_type} 不适合重试，直接失败")
                    return None
                
                if attempt < max_retry - 1:
                    # 根据错误类型调整重试延迟
                    adjusted_delay = self._get_retry_delay(error_type, DB_CONFIG["retry_delay"], attempt)
                    logger.info(f"⏳ [{fund_name}] {adjusted_delay} 秒后重试...")
                    time.sleep(adjusted_delay)
                else:
                    logger.error(f"💥 [{fund_name}] 所有重试均失败")
                    return None
        
        logger.error(f"[{fund_name}] {func_name} 拉取数据失败，超过最大重试次数")
        return None
    
    # 错误处理方法已移至基类 BaseDataProcessor
    
    def get_price_column(self, fund_type: str, df_columns) -> Optional[str]:
        """根据基金类型获取价格列名"""
        config = FUND_TYPES.get(fund_type, {})
        pattern = config.get("price_column_pattern", "")
        
        if pattern == "现价":
            return "现价" if "现价" in df_columns else None
        else:
            return next((c for c in df_columns if pattern in c), None)
    
    def extract_fund_values(self, df, fund_type: str) -> List[Tuple]:
        """提取基金数据"""
        records = []
        price_col = self.get_price_column(fund_type, df.columns)
        
        if not price_col:
            logger.warning(f"[{fund_type}] 未找到价格列")
            return records
        
        # 过滤价格不为空的数据
        filtered_df = df[df[price_col].notna()]
        logger.info(f"[{fund_type}] 价格不为空的数据条数: {len(filtered_df)}")
        
        for _, row in filtered_df.iterrows():
            code = row.get("基金代码") or row.get("代码") or ""
            name = row.get("基金简称") or row.get("名称") or ""
            price = self.safe_float(row.get(price_col, None))
            if code and name:  # 确保编码和名称不为空
                records.append((code, name, fund_type, price))
        
        return records
    
    def safe_float(self, val) -> Optional[float]:
        """安全转换为浮点数"""
        try:
            return float(val)
        except Exception:
            return None
    
    def collect_all_fund_data(self) -> Optional[Dict[str, List[Tuple]]]:
        """收集所有基金数据 - 必须全部成功才能继续"""
        fund_data = {}
        required_types = set(FUND_TYPES.keys())
        success_types = set()
        failed_types = []
        
        logger.info("=" * 60)
        logger.info("🚀 开始收集基金数据")
        logger.info(f"📋 必须获取全部 {len(required_types)} 个类型: {list(required_types)}")
        logger.info("=" * 60)
        
        for fund_name, get_func, concurrency in self.fund_tasks:
            logger.info(f"📥 正在获取: {fund_name}")
            df = self.safe_get_data(get_func, fund_name)
            
            if df is None or df.empty:
                logger.error(f"❌ [{fund_name}] 数据获取失败或为空")
                failed_types.append(fund_name)
                continue
            
            # 内存优化：分块处理大数据集
            chunk_size = 5000  # 基金数据相对较小，使用5000条记录为一块
            total_rows = len(df)
            
            if total_rows > chunk_size:
                logger.info(f"📦 [{fund_name}] 大数据集检测，启用分块处理模式 (chunk_size={chunk_size})")
                
                all_records = []
                # 分块处理
                for i in range(0, total_rows, chunk_size):
                    chunk_end = min(i + chunk_size, total_rows)
                    chunk_df = df.iloc[i:chunk_end]
                    
                    logger.info(f"📦 [{fund_name}] 处理数据块 {i//chunk_size + 1}/{(total_rows-1)//chunk_size + 1} ({i+1}-{chunk_end})")
                    
                    chunk_records = self.extract_fund_values(chunk_df, fund_name)
                    all_records.extend(chunk_records)
                    
                    # 清理临时变量
                    del chunk_df, chunk_records
                
                records = all_records
                del all_records
            else:
                # 小数据集直接处理
                records = self.extract_fund_values(df, fund_name)
            
            # 清理DataFrame
            del df
            
            if records:
                fund_data[fund_name] = records
                success_types.add(fund_name)
                logger.info(f"✅ [{fund_name}] 成功获取 {len(records)} 条记录")
            else:
                logger.error(f"❌ [{fund_name}] 提取数据失败，无有效记录")
                failed_types.append(fund_name)
        
        # 检查是否所有类型都成功获取
        logger.info("-" * 40)
        logger.info("📊 数据收集结果统计")
        logger.info("-" * 40)
        
        if success_types == required_types:
            logger.info(f"🎉 所有基金类型数据获取成功！")
            logger.info(f"✅ 成功类型: {list(success_types)} ({len(success_types)}/{len(required_types)})")
            logger.info("=" * 60)
            return fund_data
        else:
            missing_types = required_types - success_types
            logger.error(f"❌ 基金数据获取不完整，无法继续处理")
            logger.error(f"✅ 成功获取: {list(success_types)} ({len(success_types)}/{len(required_types)})")
            logger.error(f"❌ 获取失败: {list(missing_types)}")
            logger.error(f"📝 失败详情: {failed_types}")
            logger.error("🛑 由于数据不完整，将终止后续操作")
            logger.error("💡 请检查网络连接和API接口状态")
            logger.info("=" * 60)
            return None
    
    def integrate_fund_data(self, fund_data: Dict[str, List[Tuple]]) -> Tuple[List[Tuple], Set[str]]:
        """整合基金数据，处理重复编码"""
        logger.info("=" * 60)
        logger.info("🔄 开始整合基金数据，处理重复编码")
        logger.info("=" * 60)
        
        # 第一步：合并非QDII基金数据，并去除价格为空的数据
        domestic_funds = []
        domestic_codes = set()
        domestic_type_counts = {}  # 统计各类型数量
        
        empty_price_codes = set()  # 收集价格为空的编码
        
        for fund_type in ["场内基金", "开放基金", "货币基金"]:
            if fund_type in fund_data:
                type_records = fund_data[fund_type]
                logger.info(f"📊 {fund_type}: {len(type_records)} 条记录")
                
                type_count = 0
                for record in type_records:
                    code, name, _, price = record
                    if price is not None:  # 只保留价格不为空的数据
                        domestic_funds.append((code, name, fund_type, price))
                        domestic_codes.add(code)
                        type_count += 1
                    else:
                        empty_price_codes.add(code)
                
                domestic_type_counts[fund_type] = type_count
                
                # 内存优化：清理已处理的数据
                del fund_data[fund_type]
        
        # 统一打印价格为空的编码集合
        if empty_price_codes:
            logger.info(f"🔄 排除价格为空的基金编码集合 ({len(empty_price_codes)} 个): {sorted(empty_price_codes)}")
        
        logger.info(f"📊 非QDII基金（价格不为空）: {len(domestic_funds)} 条")
        logger.info(f"📊 非QDII基金编码集合: {len(domestic_codes)} 个")
        logger.info("📋 非QDII基金各类型统计:")
        for fund_type, count in domestic_type_counts.items():
            logger.info(f"     {fund_type}: {count} 条")
        
        # 第二步：QDII基金作为补充，只添加不存在的基金
        qdii_funds = []
        qdii_supplemented = 0
        qdii_skipped = 0
        qdii_type_counts = {}  # 统计各类型数量
        
        for fund_type in ["欧美QDII", "亚洲QDII"]:
            if fund_type in fund_data:
                type_records = fund_data[fund_type]
                logger.info(f"📊 {fund_type}: {len(type_records)} 条记录")
                
                type_supplemented = 0
                type_skipped = 0
                
                for record in type_records:
                    code, name, _, price = record
                    if code not in domestic_codes:
                        # 编码不存在，添加这条QDII基金
                        qdii_funds.append((code, name, fund_type, price))
                        domestic_codes.add(code)
                        qdii_supplemented += 1
                        type_supplemented += 1
                        logger.info(f"➕ 补充QDII基金: {code} ({name}) - {fund_type}")
                    else:
                        # 编码已存在，跳过这条QDII基金
                        qdii_skipped += 1
                        type_skipped += 1
                        logger.info(f"⏭️  跳过QDII基金: {code} ({name}) - {fund_type} (编码已存在)")
                
                qdii_type_counts[fund_type] = {
                    'supplemented': type_supplemented,
                    'skipped': type_skipped
                }
                
                # 内存优化：清理已处理的数据
                del fund_data[fund_type]
        
        logger.info(f"📊 QDII基金补充: {qdii_supplemented} 条")
        logger.info(f"📊 QDII基金跳过: {qdii_skipped} 条")
        logger.info("📋 QDII基金各类型统计:")
        for fund_type, counts in qdii_type_counts.items():
            logger.info(f"     {fund_type}: 补充 {counts['supplemented']} 条, 跳过 {counts['skipped']} 条")
        
        # 最终集合
        final_funds = domestic_funds + qdii_funds
        
        # 统计各类型基金数量
        type_counts = {}
        for fund in final_funds:
            fund_type = fund[2]  # fund[2]是基金类型
            type_counts[fund_type] = type_counts.get(fund_type, 0) + 1
        
        logger.info("=" * 60)
        logger.info(f"🎯 数据整合完成！最终基金集合: {len(final_funds)} 条")
        logger.info(f"   - 非QDII基金: {len(domestic_funds)} 条")
        logger.info(f"   - QDII补充基金: {len(qdii_funds)} 条")
        logger.info(f"   - 总编码数: {len(domestic_codes)} 个")
        
        # 显示各类型基金详细统计
        logger.info("📊 各类型基金详细统计:")
        for fund_type, count in sorted(type_counts.items()):
            logger.info(f"     {fund_type}: {count} 条")
        
        logger.info("=" * 60)
        
        return final_funds, domestic_codes
    
    def analyze_data_differences(self, final_funds: List[Tuple], existing_codes: Set[str]) -> Tuple[Set[str], Set[str], Set[str]]:
        """分析数据差异，返回新增、删除、更新的基金编码集合"""
        self.log_section_start("🔍 开始分析数据差异")
        
        final_codes = {f[0] for f in final_funds}
        new_codes = final_codes - existing_codes  # 新增：在最终数据中但不在数据库中
        removed_codes = existing_codes - final_codes  # 删除：在数据库中但不在最终数据中
        update_codes = final_codes & existing_codes  # 更新：既在最终数据中也在数据库中
        
        logger.info(f"📊 数据统计:")
        logger.info(f"   - 最终基金集合: {len(final_funds)} 条")
        logger.info(f"   - 数据库现有: {len(existing_codes)} 条")
        logger.info(f"   - 新增基金: {len(new_codes)} 条")
        logger.info(f"   - 更新基金: {len(update_codes)} 条")
        logger.info(f"   - 需要删除: {len(removed_codes)} 条")
        
        # 输出示例数据
        if new_codes:
            logger.info(f"🆕 新增基金编码示例: {list(new_codes)[:5]}")
            if len(new_codes) > 5:
                logger.info(f"   ... 还有 {len(new_codes) - 5} 个编码")
        else:
            logger.info("✅ 无新增基金编码")
            
        if update_codes:
            logger.info(f"🔄 更新基金编码示例: {list(update_codes)[:5]}")
            if len(update_codes) > 5:
                logger.info(f"   ... 还有 {len(update_codes) - 5} 个编码")
        else:
            logger.info("✅ 无需更新基金编码")
            
        if removed_codes:
            logger.info(f"🗑️  需要删除的基金编码示例: {list(removed_codes)[:5]}")
            if len(removed_codes) > 5:
                logger.info(f"   ... 还有 {len(removed_codes) - 5} 个编码")
        else:
            logger.info("✅ 无需删除基金编码")
        
        return new_codes, removed_codes, update_codes
    
    def get_data_sources(self) -> List[Dict[str, Any]]:
        """获取数据源配置"""
        sources = []
        for fund_type, func, concurrency in self.fund_tasks:
            config = FUND_TYPES.get(fund_type, {})
            sources.append({
                'name': fund_type,
                'api_func': func,
                'clean_func': self.extract_fund_values,
                'concurrency': concurrency,
                'batch_size': DB_CONFIG.get('batch_size', 1000)
            })
        return sources
    
    def process_data(self, data: Any, fund_type: str) -> Optional[List[Tuple]]:
        """处理数据"""
        # 基金数据处理逻辑已在extract_fund_values中实现
        # 这里返回原始数据，实际处理在extract_fund_values中进行
        return data
    
    def sync_to_database(self, data: List[Tuple], fund_type: str, db_connection) -> Dict[str, Any]:
        """同步数据到数据库"""
        # 基金数据同步逻辑需要在具体实现中完成
        # 这里返回基本统计信息
        return {
            "total_records": len(data),
            "fund_type": fund_type,
            "status": "success"
        }
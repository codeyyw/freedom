# -*- coding: utf-8 -*-
"""
数据处理器抽象基类
提供统一的数据处理接口和通用功能
"""

import logging
import time
from abc import ABC, abstractmethod
from typing import Dict, List, Set, Tuple, Optional, Any

logger = logging.getLogger(__name__)

class BaseDataProcessor(ABC):
    """数据处理器抽象基类"""
    
    def __init__(self):
        """初始化基类"""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.start_time = None
        
    @abstractmethod
    def get_data_sources(self) -> List[Dict[str, Any]]:
        """获取数据源配置"""
        pass
    
    @abstractmethod
    def safe_get_data(self, get_func, source_name: str, **kwargs) -> Optional[Any]:
        """安全获取数据"""
        pass
    
    @abstractmethod
    def process_data(self, raw_data: Any, source_name: str) -> Optional[List[Tuple]]:
        """处理数据"""
        pass
    
    @abstractmethod
    def sync_to_database(self, processed_data: Dict[str, List[Tuple]]) -> Dict[str, Any]:
        """同步数据到数据库"""
        pass
    
    def format_duration(self, duration_sec: float) -> str:
        """格式化时间间隔"""
        if duration_sec < 60:
            return f"{duration_sec:.2f} 秒"
        elif duration_sec < 3600:
            minutes = int(duration_sec // 60)
            seconds = duration_sec % 60
            return f"{minutes} 分 {seconds:.2f} 秒"
        else:
            hours = int(duration_sec // 3600)
            minutes = int((duration_sec % 3600) // 60)
            seconds = duration_sec % 60
            return f"{hours} 小时 {minutes} 分 {seconds:.2f} 秒"
    
    def _classify_error(self, error: Exception) -> str:
        """错误分类"""
        error_str = str(error).lower()
        error_type = type(error).__name__
        
        # 编码相关错误（基金模块特有）
        if "chunkedencodingerror" in error_type.lower() or "chunked encoding" in error_str:
            return "CHUNKED_ENCODING"
        
        # 超时错误
        if any(keyword in error_str for keyword in ['timeout', 'timed out']):
            return 'TIMEOUT'
        
        # 网络连接错误
        if any(keyword in error_str for keyword in ['connection', 'network', 'unreachable']):
            return 'NETWORK'
        
        # API限制错误
        if any(keyword in error_str for keyword in ['rate limit', 'too many requests', '429']):
            return 'RATE_LIMIT'
        
        # 服务器错误
        if any(keyword in error_str for keyword in ['500', '502', '503', '504', 'server error']):
            return 'SERVER_ERROR'
        
        # 权限错误
        if any(keyword in error_str for keyword in ['unauthorized', 'forbidden', '401', '403']):
            return 'AUTH_ERROR'
        
        # 资源未找到错误
        if any(keyword in error_str for keyword in ['not found', '404']):
            return 'NOT_FOUND'
        
        # 数据为空错误
        if any(keyword in error_str for keyword in ['empty', 'no data']):
            return 'NO_DATA'
        
        # Pandas数据不匹配错误（基金模块特有）
        if "length mismatch" in error_str and "expected axis has 0 elements" in error_str:
            return "PANDAS_MISMATCH"
        
        # 数据格式错误
        if any(keyword in error_str for keyword in ['json', 'parse', 'decode', 'format']):
            return 'DATA_FORMAT_ERROR'
        
        # 数据库错误
        if 'database' in error_str or error_type in ['DatabaseError', 'OperationalError']:
            return 'DATABASE_ERROR'
        
        # 其他未知错误
        return 'UNKNOWN'
    
    def _should_retry(self, error_type: str, attempt: int, max_retry: int) -> bool:
        """判断是否应该重试"""
        if attempt >= max_retry:
            return False
        
        # 不重试的错误类型
        no_retry_errors = {'AUTH_ERROR', 'NOT_FOUND', 'DATA_FORMAT_ERROR'}
        if error_type in no_retry_errors:
            return False
        
        # 限制重试次数的错误类型
        if error_type == 'RATE_LIMIT' and attempt >= 2:
            return False
        
        return True
    
    def _get_retry_delay(self, error_type: str, base_delay: int, attempt: int) -> int:
        """获取重试延迟时间"""
        # 根据错误类型调整延迟
        if error_type == 'RATE_LIMIT':
            return base_delay * (2 ** attempt) + 5  # 指数退避 + 额外延迟
        elif error_type == 'CHUNKED_ENCODING':
            return base_delay + 2  # 编码错误稍微延迟
        elif error_type == 'TIMEOUT':
            return base_delay + attempt  # 线性增加
        elif error_type == 'NETWORK':
            return base_delay * attempt  # 线性增长
        elif error_type == 'SERVER_ERROR':
            return base_delay * 2  # 服务器错误延迟更久
        elif error_type == 'PANDAS_MISMATCH':
            return base_delay * (attempt + 1)  # pandas错误增加等待时间
        else:
            return base_delay
    
    def start_timing(self):
        """开始计时"""
        self.start_time = time.time()
    
    def get_elapsed_time(self) -> float:
        """获取已用时间"""
        if self.start_time is None:
            return 0.0
        return time.time() - self.start_time
    
    def log_performance(self, operation: str, duration: float, count: int = None):
        """记录性能日志"""
        if count is not None:
            rate = count / duration if duration > 0 else 0
            self.logger.info(f"📊 {operation}: {count} 条记录, 耗时 {self.format_duration(duration)}, 速率 {rate:.1f} 条/秒")
        else:
            self.logger.info(f"📊 {operation}: 耗时 {self.format_duration(duration)}")
    
    def log_section_start(self, title: str, level: str = "info"):
        """记录章节开始日志，避免重复分隔线"""
        getattr(self.logger, level)(f"🚀 {title}")
    
    def log_section_end(self, title: str, duration: float = None, level: str = "info"):
        """记录章节结束日志"""
        if duration is not None:
            getattr(self.logger, level)(f"✅ {title} - 耗时 {self.format_duration(duration)}")
        else:
            getattr(self.logger, level)(f"✅ {title}")
    
    def log_separator(self, char: str = "=", length: int = 60, message: str = None):
        """记录分隔线（仅在必要时使用）"""
        if message:
            padding = (length - len(message) - 2) // 2
            separator = char * padding + f" {message} " + char * padding
            if len(separator) < length:
                separator += char
        else:
            separator = char * length
        self.logger.info(separator)
    
    def run(self) -> Dict[str, Any]:
        """运行数据处理流程"""
        self.start_timing()
        
        try:
            # 1. 获取数据源配置
            data_sources = self.get_data_sources()
            self.logger.info(f"📋 配置了 {len(data_sources)} 个数据源")
            
            # 2. 收集所有数据
            all_data = {}
            for source_config in data_sources:
                source_name = source_config['name']
                api_func = source_config['api_func']
                
                self.logger.info(f"📥 正在获取 {source_name} 数据...")
                raw_data = self.safe_get_data(api_func, source_name)
                
                if raw_data is not None:
                    processed_data = self.process_data(raw_data, source_name)
                    if processed_data:
                        all_data[source_name] = processed_data
                        self.logger.info(f"✅ {source_name}: 获取 {len(processed_data)} 条记录")
                    else:
                        self.logger.error(f"❌ {source_name}: 数据处理失败")
                        return {'success': False, 'error': f'{source_name} 数据处理失败'}
                else:
                    self.logger.error(f"❌ {source_name}: 数据获取失败")
                    return {'success': False, 'error': f'{source_name} 数据获取失败'}
            
            # 3. 同步到数据库
            if all_data:
                sync_result = self.sync_to_database(all_data)
                
                # 4. 记录总体性能
                total_time = self.get_elapsed_time()
                self.log_performance("总体处理", total_time)
                
                return {
                    'success': True,
                    'processed_sources': len(all_data),
                    'total_time': total_time,
                    'sync_result': sync_result
                }
            else:
                self.logger.error("❌ 没有获取到任何有效数据")
                return {'success': False, 'error': '没有获取到任何有效数据'}
                
        except Exception as e:
            self.logger.error(f"❌ 数据处理流程异常: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}
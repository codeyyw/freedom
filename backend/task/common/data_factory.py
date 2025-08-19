# -*- coding: utf-8 -*-
"""
数据工厂模式
统一管理数据源和清洗函数的创建
"""

import logging
from typing import Dict, List, Callable, Any, Optional
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class DataSourceConfig:
    """数据源配置类"""
    
    def __init__(self, name: str, api_func: Callable, clean_func: Callable, 
                 concurrency: int = 1, batch_size: int = 1000, **kwargs):
        self.name = name
        self.api_func = api_func
        self.clean_func = clean_func
        self.concurrency = concurrency
        self.batch_size = batch_size
        self.extra_config = kwargs
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'name': self.name,
            'api_func': self.api_func,
            'clean_func': self.clean_func,
            'concurrency': self.concurrency,
            'batch_size': self.batch_size,
            **self.extra_config
        }

class BaseDataFactory(ABC):
    """数据工厂抽象基类"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self._data_sources = {}
        self._clean_functions = {}
    
    @property
    def data_sources(self) -> Dict[str, DataSourceConfig]:
        """获取数据源配置"""
        return self._data_sources
    
    @abstractmethod
    def register_data_sources(self):
        """注册数据源"""
        pass
    
    @abstractmethod
    def register_clean_functions(self):
        """注册清洗函数"""
        pass
    
    def add_data_source(self, config: DataSourceConfig):
        """添加数据源配置"""
        self._data_sources[config.name] = config
        self.logger.debug(f"注册数据源: {config.name}")
    
    def add_clean_function(self, name: str, func: Callable):
        """添加清洗函数"""
        self._clean_functions[name] = func
        self.logger.debug(f"注册清洗函数: {name}")
    
    def get_data_source(self, name: str) -> Optional[DataSourceConfig]:
        """获取数据源配置"""
        return self._data_sources.get(name)
    
    def get_clean_function(self, name: str) -> Optional[Callable]:
        """获取清洗函数"""
        return self._clean_functions.get(name)
    
    def get_all_data_sources(self) -> List[DataSourceConfig]:
        """获取所有数据源配置"""
        return list(self._data_sources.values())
    
    def get_data_source_names(self) -> List[str]:
        """获取所有数据源名称"""
        return list(self._data_sources.keys())
    
    def get_clean_function_names(self) -> List[str]:
        """获取所有清洗函数名称"""
        return list(self._clean_functions.keys())
    
    def validate_configuration(self) -> bool:
        """验证配置完整性"""
        if not self._data_sources:
            self.logger.error("❌ 没有注册任何数据源")
            return False
        
        # 检查每个数据源是否有对应的清洗函数（允许清洗函数为None）
        for source_name, source_config in self._data_sources.items():
            if source_config.clean_func is None:
                self.logger.debug(f"📝 数据源 {source_name} 的清洗函数为空，将在数据处理器中实现")
            else:
                clean_func_name = getattr(source_config.clean_func, '__name__', str(source_config.clean_func))
                if clean_func_name not in self._clean_functions:
                    self.logger.warning(f"⚠️ 数据源 {source_name} 的清洗函数 {clean_func_name} 未在工厂中注册")
        
        self.logger.info(f"✅ 配置验证通过: {len(self._data_sources)} 个数据源, {len(self._clean_functions)} 个清洗函数")
        return True
    
    def initialize(self) -> bool:
        """初始化工厂"""
        try:
            self.logger.info("🏭 正在初始化数据工厂...")
            
            # 注册数据源和清洗函数
            self.register_data_sources()
            self.register_clean_functions()
            
            # 验证配置
            if self.validate_configuration():
                self.logger.info("🎉 数据工厂初始化成功")
                return True
            else:
                self.logger.error("❌ 数据工厂初始化失败：配置验证不通过")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ 数据工厂初始化异常: {e}", exc_info=True)
            return False
    
    def create_processor_config(self) -> List[Dict[str, Any]]:
        """为数据处理器创建配置"""
        if not self.validate_configuration():
            raise ValueError("工厂配置无效，无法创建处理器配置")
        
        configs = []
        for source_config in self._data_sources.values():
            configs.append(source_config.to_dict())
        
        return configs
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取工厂统计信息"""
        return {
            'data_sources_count': len(self._data_sources),
            'clean_functions_count': len(self._clean_functions),
            'data_source_names': self.get_data_source_names(),
            'clean_function_names': self.get_clean_function_names()
        }

class StockDataFactory(BaseDataFactory):
    """股票数据工厂"""
    
    def register_data_sources(self):
        """注册股票数据源"""
        # 导入股票相关模块
        import akshare as ak
        
        # 简化的数据源注册，不依赖具体的清洗函数
        # 注册A股数据源
        self.add_data_source(DataSourceConfig(
            name="A股",
            api_func=ak.stock_zh_a_spot_em,
            clean_func=None,  # 清洗函数在具体处理器中实现
            concurrency=2,
            batch_size=1500
        ))
        
        # 注册港股数据源
        self.add_data_source(DataSourceConfig(
            name="港股",
            api_func=ak.stock_hk_spot_em,
            clean_func=None,
            concurrency=1,
            batch_size=1500
        ))
        
        # 注册美股数据源
        self.add_data_source(DataSourceConfig(
            name="美股",
            api_func=ak.stock_us_spot_em,
            clean_func=None,
            concurrency=4,
            batch_size=1500
        ))
    
    def register_clean_functions(self):
        """注册股票清洗函数"""
        # 清洗函数在具体的数据处理器中实现，这里不需要注册
        pass

class FundDataFactory(BaseDataFactory):
    """基金数据工厂"""
    
    def register_data_sources(self):
        """注册基金数据源"""
        import akshare as ak
        
        # 注册开放基金数据源
        config = DataSourceConfig(
            name="开放基金",
            api_func=ak.fund_open_fund_daily_em,
            clean_func=None,
            concurrency=4,
            batch_size=1000
        )
        config.price_column_pattern = "单位净值"
        self.add_data_source(config)
        
        # 注册货币基金数据源
        config = DataSourceConfig(
            name="货币基金",
            api_func=ak.fund_money_fund_daily_em,
            clean_func=None,
            concurrency=1,
            batch_size=1000
        )
        config.price_column_pattern = "万份收益"
        self.add_data_source(config)
        
        # 注册场内基金数据源
        config = DataSourceConfig(
            name="场内基金",
            api_func=ak.fund_etf_fund_daily_em,
            clean_func=None,
            concurrency=1,
            batch_size=1000
        )
        config.price_column_pattern = "单位净值"
        self.add_data_source(config)
        
        # 注册欧美QDII数据源
        config = DataSourceConfig(
            name="欧美QDII",
            api_func=ak.qdii_e_index_jsl,
            clean_func=None,
            concurrency=1,
            batch_size=1000
        )
        config.price_column_pattern = "现价"
        self.add_data_source(config)
        
        # 注册亚洲QDII数据源
        config = DataSourceConfig(
            name="亚洲QDII",
            api_func=ak.qdii_a_index_jsl,
            clean_func=None,
            concurrency=1,
            batch_size=1000
        )
        config.price_column_pattern = "现价"
        self.add_data_source(config)
    
    def register_clean_functions(self):
        """注册基金清洗函数"""
        # 基金使用统一的清洗逻辑，在数据处理器中实现
        self.add_clean_function("extract_fund_values", self._extract_fund_values)
    
    def _get_fund_clean_function(self, fund_type: str):
        """获取基金清洗函数"""
        # 返回一个通用的基金清洗函数引用
        return self._extract_fund_values
    
    def _extract_fund_values(self, df, fund_type: str):
        """提取基金数据值（占位符函数）"""
        # 这个函数在实际使用时会被数据处理器中的实现替换
        return []

def create_data_factory(factory_type: str) -> Optional[BaseDataFactory]:
    """工厂创建函数"""
    factories = {
        'stock': StockDataFactory,
        'fund': FundDataFactory
    }
    
    factory_class = factories.get(factory_type.lower())
    if factory_class:
        factory = factory_class()
        if factory.initialize():
            return factory
        else:
            logger.error(f"❌ {factory_type} 数据工厂初始化失败")
            return None
    else:
        logger.error(f"❌ 未知的工厂类型: {factory_type}")
        return None
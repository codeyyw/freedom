"""
基金数据同步模块

该模块提供基金数据的获取、处理和存储功能。
"""

# 暴露主要方法
from .index import sync_task_runner

__all__ = ['sync_task_runner']
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQL查询统一管理模块
集中管理项目中实际使用的SQL语句
"""

from sqlalchemy import text

# ============================================================================
# 股票数据相关SQL
# ============================================================================

class StockSQL:
    """股票数据相关SQL语句"""
    
    # 查询现有股票代码
    GET_EXISTING_SYMBOLS = text("""
        SELECT symbol, market 
        FROM stock_info 
        WHERE status = 'L'
    """)
    
    # 更新股票信息
    UPDATE_STOCK = text("""
        UPDATE stock_info SET
            price = :price,
            diff = :diff,
            chg = :chg,
            best_bid_price = :best_bid_price,
            best_ask_price = :best_ask_price,
            preclose = :preclose,
            open = :open,
            high = :high,
            low = :low,
            volume = :volume,
            turnover = :turnover,
            mktcap = :mktcap,
            pe = :pe,
            datetime = :datetime
        WHERE symbol = :symbol AND market = :market
    """)
    
    # 插入新股票
    INSERT_STOCK = text("""
        INSERT INTO stock_info (
            symbol, cname, name, category, category_id, market, status,
            price, diff, chg, preclose, open, high, low, amplitude,
            volume, turnover, mktcap, pe,
            best_bid_price, best_ask_price, datetime
        )
        VALUES (
            :symbol, :cname, :name, :category, :category_id, :market, :status,
            :price, :diff, :chg, :preclose, :open, :high, :low, :amplitude,
            :volume, :turnover, :mktcap, :pe,
            :best_bid_price, :best_ask_price, :datetime
        )
    """)
    
    # 标记股票为删除状态
    MARK_STOCKS_DELETED = text("""
        UPDATE stock_info 
        SET status = 'D'
        WHERE symbol = ANY(:symbols) AND market = :market
    """)

# ============================================================================
# 基金数据相关SQL
# ============================================================================

class FundSQL:
    """基金数据相关SQL语句"""
    
    # 查询现有基金编码
    GET_EXISTING_FUND_CODES = text("""
        SELECT fund_code 
        FROM fund_info 
        WHERE status = 'L'
    """)
    
    # 标记基金为删除状态
    MARK_FUNDS_DELETED = text("""
        UPDATE fund_info 
        SET status = 'D'
        WHERE fund_code = ANY(:codes) AND status = 'L'
    """)
    
    # 批量插入基金
    INSERT_FUNDS_BATCH = """
        INSERT INTO fund_info(fund_code, fund_name, fund_type, latest_price, status)
        VALUES %s
    """
    
    # 批量更新基金
    UPDATE_FUNDS_BATCH = """
        UPDATE fund_info 
        SET fund_name = data.fund_name, 
            latest_price = data.latest_price
        FROM (VALUES %s) AS data(fund_code, fund_name, latest_price)
        WHERE fund_info.fund_code = data.fund_code 
          AND fund_info.status = 'L'
    """

# ============================================================================
# 导出SQL类
# ============================================================================

__all__ = ['StockSQL', 'FundSQL']
import pandas as pd
from datetime import datetime

def clean_a_stock_data(dataframe):
    """清洗A股股票数据"""
    today_str = datetime.now().strftime("%Y-%m-%d")
    datetime_series = pd.to_datetime(today_str + ' ' + dataframe["时间戳"], errors='coerce')

    cleaned_dataframe = pd.DataFrame({
        "symbol": dataframe["代码"].astype(str),
        "cname": dataframe.get("名称", pd.Series([""]*len(dataframe))).astype(str),
        "name": dataframe.get("名称", pd.Series([""]*len(dataframe))).astype(str),
        "price": pd.to_numeric(dataframe["最新价"], errors="coerce"),
        "diff": pd.to_numeric(dataframe["涨跌额"], errors="coerce"),
        "chg": pd.to_numeric(dataframe["涨跌幅"], errors="coerce"),
        "best_bid_price": pd.to_numeric(dataframe["买入"], errors="coerce"),
        "best_ask_price": pd.to_numeric(dataframe["卖出"], errors="coerce"),
        "preclose": pd.to_numeric(dataframe["昨收"], errors="coerce"),
        "open": pd.to_numeric(dataframe["今开"], errors="coerce"),
        "high": pd.to_numeric(dataframe["最高"], errors="coerce"),
        "low": pd.to_numeric(dataframe["最低"], errors="coerce"),
        "volume": pd.to_numeric(dataframe["成交量"], errors="coerce").fillna(0).astype(int),
        "turnover": pd.to_numeric(dataframe["成交额"], errors="coerce"),
        "datetime": datetime_series,
        "category": None,
        "category_id": None,
        "amplitude": None,
        "mktcap": None,
        "pe": None,
        "market": "A股",
        "status": "L"
    })
    return cleaned_dataframe.dropna(subset=["symbol", "datetime"])

def clean_hk_stock_data(dataframe):
    """清洗港股股票数据"""
    datetime_series = pd.to_datetime(dataframe['日期时间'], errors='coerce')
    cleaned_dataframe = pd.DataFrame({
        "symbol": dataframe["代码"].astype(str),
        "cname": dataframe.get("中文名称", pd.Series([""] * len(dataframe))).astype(str),
        "name": dataframe.get("英文名称", pd.Series([""] * len(dataframe))).astype(str),
        "price": pd.to_numeric(dataframe["最新价"], errors="coerce"),
        "diff": pd.to_numeric(dataframe["涨跌额"], errors="coerce"),
        "chg": pd.to_numeric(dataframe["涨跌幅"], errors="coerce"),
        "best_bid_price": pd.to_numeric(dataframe["买一"], errors="coerce"),
        "best_ask_price": pd.to_numeric(dataframe["卖一"], errors="coerce"),
        "preclose": pd.to_numeric(dataframe["昨收"], errors="coerce"),
        "open": pd.to_numeric(dataframe["今开"], errors="coerce"),
        "high": pd.to_numeric(dataframe["最高"], errors="coerce"),
        "low": pd.to_numeric(dataframe["最低"], errors="coerce"),
        "volume": pd.to_numeric(dataframe["成交量"], errors="coerce").fillna(0).astype(int),
        "turnover": pd.to_numeric(dataframe["成交额"], errors="coerce"),
        "datetime": datetime_series,
        "category": None,
        "category_id": None,
        "amplitude": None,
        "mktcap": None,
        "pe": None,
        "market": "港股",
        "status": "L"
    })
    return cleaned_dataframe.dropna(subset=["symbol", "datetime"])

def clean_us_stock_data(dataframe):
    """清洗美股股票数据"""
    from datetime import datetime
    current_datetime = datetime.now()
    amplitude_float = dataframe["amplitude"].str.rstrip('%').astype(float) if "amplitude" in dataframe.columns else None
    cleaned_dataframe = pd.DataFrame({
        "symbol": dataframe["symbol"].astype(str),
        "cname": dataframe.get("cname", pd.Series([""]*len(dataframe))).astype(str),
        "name": dataframe.get("name", pd.Series([""]*len(dataframe))).astype(str),
        "category": dataframe.get("category", None),
        "category_id": pd.to_numeric(dataframe.get("category_id", pd.Series([None]*len(dataframe))), errors="coerce").fillna(0).astype(int),
        "price": pd.to_numeric(dataframe["price"], errors="coerce"),
        "diff": pd.to_numeric(dataframe["diff"], errors="coerce"),
        "chg": pd.to_numeric(dataframe["chg"], errors="coerce"),
        "preclose": pd.to_numeric(dataframe["preclose"], errors="coerce"),
        "open": pd.to_numeric(dataframe["open"], errors="coerce"),
        "high": pd.to_numeric(dataframe["high"], errors="coerce"),
        "low": pd.to_numeric(dataframe["low"], errors="coerce"),
        "amplitude": amplitude_float,
        "volume": pd.to_numeric(dataframe["volume"], errors="coerce").fillna(0).astype(int),
        "mktcap": pd.to_numeric(dataframe.get("mktcap", None), errors="coerce"),
        "pe": pd.to_numeric(dataframe.get("pe", None), errors="coerce"),
        "datetime": current_datetime,
        "best_bid_price": None,
        "best_ask_price": None,
        "turnover": None,
        "market": "美股",
        "status": "L"
    })
    return cleaned_dataframe.dropna(subset=["symbol"])

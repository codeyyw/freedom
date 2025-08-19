import datetime

def is_time_between(start_time, end_time, check_time=None, tolerance_seconds=30):
    """检查时间是否在指定区间内，支持容错时间"""
    if check_time is None:
        check_time = datetime.datetime.now().time()
    
    # 将时间转换为秒数进行计算，便于处理容错
    def time_to_seconds(t):
        return t.hour * 3600 + t.minute * 60 + t.second
    
    start_seconds = time_to_seconds(start_time) - tolerance_seconds
    end_seconds = time_to_seconds(end_time) + tolerance_seconds
    check_seconds = time_to_seconds(check_time)
    
    if start_time <= end_time:
        # 正常时间区间
        return start_seconds <= check_seconds <= end_seconds
    else:
        # 跨日时间区间
        return check_seconds >= start_seconds or check_seconds <= end_seconds

def is_a_stock_market_open(now=None, tolerance_seconds=30):
    """检查A股市场是否开盘"""
    if now is None:
        now = datetime.datetime.now().time()
    return is_time_between(datetime.time(9, 30), datetime.time(11, 30), now, tolerance_seconds) or \
           is_time_between(datetime.time(13, 0), datetime.time(15, 0), now, tolerance_seconds)

def is_hk_stock_market_open(now=None, tolerance_seconds=30):
    """检查港股市场是否开盘"""
    if now is None:
        now = datetime.datetime.now().time()
    return is_time_between(datetime.time(9, 30), datetime.time(12, 0), now, tolerance_seconds) or \
           is_time_between(datetime.time(13, 0), datetime.time(16, 0), now, tolerance_seconds)

def is_us_stock_market_open(now=None, is_dst=True, tolerance_seconds=30):
    """检查美股市场是否开盘"""
    if now is None:
        now = datetime.datetime.now().time()
    if is_dst:
        return is_time_between(datetime.time(21, 30), datetime.time(23, 59, 59), now, tolerance_seconds) or \
               is_time_between(datetime.time(0, 0), datetime.time(4, 0), now, tolerance_seconds)
    else:
        return is_time_between(datetime.time(22, 30), datetime.time(23, 59, 59), now, tolerance_seconds) or \
               is_time_between(datetime.time(0, 0), datetime.time(5, 0), now, tolerance_seconds)

def check_market_open_status(check_func, hours_delay=2, tolerance_seconds=30):
    """检查市场开盘状态（包括当前时间和延迟时间）"""
    current_datetime = datetime.datetime.now()
    delayed_datetime = current_datetime - datetime.timedelta(hours=hours_delay)
    current_time = current_datetime.time()
    delayed_time = delayed_datetime.time()
    is_dst = 3 <= current_datetime.month <= 11 if check_func == is_us_stock_market_open else True

    # 为所有市场检查函数传递容错时间参数
    if check_func == is_us_stock_market_open:
        open_now = check_func(current_time, is_dst, tolerance_seconds)
        open_delayed = check_func(delayed_time, is_dst, tolerance_seconds)
    else:
        open_now = check_func(current_time, tolerance_seconds)
        open_delayed = check_func(delayed_time, tolerance_seconds)
    
    return open_now or open_delayed

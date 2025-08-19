import logging
import json
from flask import Flask, jsonify, request
from config import config
from database import QueryBuilder, execute_query
from validators import RequestValidator, ResponseFormatter, ValidationError
from cache import cached, rate_limited, cache_stats, clear_cache

app = Flask(__name__)

# 配置JSON编码，确保中文字符正确显示
app.json.ensure_ascii = False

# 配置日志
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='[%(asctime)s] %(levelname)s %(name)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# 验证配置
missing_configs = config.validate()
if missing_configs:
    logger.error(f"缺少必需的配置项: {', '.join(missing_configs)}")
    raise RuntimeError(f"缺少必需的配置项: {', '.join(missing_configs)}")


@app.route("/", methods=["GET"])
def health_check():
    """健康检查接口"""
    return jsonify(ResponseFormatter.success(
        data={
            "status": "healthy",
            "service": "Stock and Fund API Service",
            "version": "2.0.0",
            "environment": config.ENVIRONMENT,
            "tables": {
                "stock": config.STOCK_TABLE,
                "fund": config.FUND_TABLE
            },
            "features": [
                "参数验证",
                "响应格式标准化",
                "数据库连接池",
                "缓存机制",
                "限流保护",
                "错误处理",
                "多环境支持"
            ],
            "endpoints": {
                "/": "健康检查",
                "/stockinfo": "股票信息查询 (缓存5分钟, 限流200次/分钟)",
                "/fundinfo": "基金信息查询 (缓存5分钟, 限流200次/分钟)",
                "/cache/stats": "缓存统计信息 (限流50次/分钟)",
                "/cache/clear": "清空缓存 (限流10次/分钟)"
            }
        },
        message="服务运行正常"
    ))


@app.route("/stockinfo", methods=["GET"])
@rate_limited(max_requests=200, window_seconds=60)
@cached(ttl=300, key_prefix="stock")
def get_stock_info():
    """股票信息查询接口"""
    try:
        # 参数验证
        params = RequestValidator.validate_stock_params()
        
        # 构建查询
        query, query_params = QueryBuilder.build_stock_query(params)
        
        # 执行查询
        result = execute_query(query, query_params, 'stock')
        
        logger.info(f"股票查询成功，返回 {len(result)} 条记录")
        return jsonify(ResponseFormatter.success(
            data=result,
            message="股票信息查询成功",
            total=len(result)
        ))
        
    except ValidationError as e:
        logger.warning(f"股票查询参数验证失败: {e.message}")
        return jsonify(ResponseFormatter.validation_error(e)), 400
        
    except Exception as e:
        logger.error(f"股票查询失败: {str(e)}")
        return jsonify(ResponseFormatter.error(
            message=f"股票查询失败: {str(e)}",
            code=500
        )), 500


@app.route("/fundinfo", methods=["GET"])
@rate_limited(max_requests=200, window_seconds=60)
@cached(ttl=300, key_prefix="fund")
def get_fund_info():
    """基金信息查询接口"""
    try:
        # 参数验证
        params = RequestValidator.validate_fund_params()
        
        # 构建查询
        query, query_params = QueryBuilder.build_fund_query(params)
        
        # 执行查询
        result = execute_query(query, query_params, 'fund')
        
        logger.info(f"基金查询成功，返回 {len(result)} 条记录")
        return jsonify(ResponseFormatter.success(
            data=result,
            message="基金信息查询成功",
            total=len(result)
        ))
        
    except ValidationError as e:
        logger.warning(f"基金查询参数验证失败: {e.message}")
        return jsonify(ResponseFormatter.validation_error(e)), 400
        
    except Exception as e:
        logger.error(f"基金查询失败: {str(e)}")
        return jsonify(ResponseFormatter.error(
            message=f"基金查询失败: {str(e)}",
            code=500
        )), 500


@app.route("/cache/stats", methods=["GET"])
@rate_limited(max_requests=50, window_seconds=60)
def get_cache_stats():
    """获取缓存统计信息"""
    try:
        stats = cache_stats()
        return jsonify(ResponseFormatter.success(
            data=stats,
            message="缓存统计信息获取成功"
        ))
    except Exception as e:
        logger.error(f"获取缓存统计失败: {str(e)}")
        return jsonify(ResponseFormatter.error(
            message=f"获取缓存统计失败: {str(e)}",
            code=500
        )), 500


@app.route("/cache/clear", methods=["POST"])
@rate_limited(max_requests=10, window_seconds=60)
def clear_cache_endpoint():
    """清空缓存"""
    try:
        clear_cache()
        return jsonify(ResponseFormatter.success(
            data=None,
            message="缓存清空成功"
        ))
    except Exception as e:
        logger.error(f"清空缓存失败: {str(e)}")
        return jsonify(ResponseFormatter.error(
            message=f"清空缓存失败: {str(e)}",
            code=500
        )), 500


# 全局错误处理器
@app.errorhandler(404)
def not_found(error):
    """404错误处理"""
    return jsonify(ResponseFormatter.error(
        message="请求的资源不存在",
        code=404
    )), 404

@app.errorhandler(405)
def method_not_allowed(error):
    """405错误处理"""
    return jsonify(ResponseFormatter.error(
        message="请求方法不被允许",
        code=405
    )), 405

@app.errorhandler(500)
def internal_error(error):
    """500错误处理"""
    logger.error(f"内部服务器错误: {str(error)}")
    return jsonify(ResponseFormatter.error(
        message="内部服务器错误",
        code=500
    )), 500

# 云函数入口点
def main(event, context):
    """云函数主入口"""
    from werkzeug.serving import WSGIRequestHandler
    
    # 设置请求处理器
    WSGIRequestHandler.protocol_version = "HTTP/1.1"
    
    # 返回Flask应用
    return app(event, context)


if __name__ == "__main__":
    # 本地开发模式
    logger.info("启动本地开发服务器...")
    app.run(host="0.0.0.0", port=8000, debug=True)
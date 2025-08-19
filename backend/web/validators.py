from typing import Dict, Any, List, Optional
from flask import request
import re

class ValidationError(Exception):
    """参数验证异常"""
    def __init__(self, message: str, field: str = None):
        self.message = message
        self.field = field
        super().__init__(message)

class RequestValidator:
    """请求参数验证器"""
    
    @staticmethod
    def validate_stock_params() -> Dict[str, Any]:
        """验证股票查询参数"""
        params = {}
        
        # market 参数验证
        market = request.args.get('market', '').strip()
        if market:
            if not re.match(r'^[A-Z]{2,10}$', market):
                raise ValidationError("市场代码格式无效，应为2-10位大写字母", "market")
            params['market'] = market
        
        # symbol 参数验证
        symbol = request.args.get('symbol', '').strip()
        if symbol:
            if not re.match(r'^[A-Z0-9]{1,20}$', symbol):
                raise ValidationError("股票代码格式无效，应为1-20位大写字母或数字", "symbol")
            params['symbol'] = symbol
        
        # name 参数验证
        name = request.args.get('name', '').strip()
        if name:
            if len(name) > 50:
                raise ValidationError("股票名称长度不能超过50个字符", "name")
            params['name'] = name
        
        # status 参数验证
        status = request.args.get('status', '').strip()
        if status:
            if status not in ['L', 'D', 'S']:
                raise ValidationError("状态参数无效，应为L、D或S", "status")
            params['status'] = status
        
        # limit 参数验证
        limit_str = request.args.get('limit', '500')
        try:
            limit = int(limit_str)
            if limit <= 0:
                raise ValidationError("限制数量必须大于0", "limit")
            if limit > 1000:
                raise ValidationError("限制数量不能超过1000", "limit")
            params['limit'] = limit
        except ValueError:
            raise ValidationError("限制数量必须为有效整数", "limit")
        
        # order 参数验证
        order = request.args.get('order', '').lower().strip()
        if order:
            if order not in ['asc', 'desc']:
                raise ValidationError("排序参数无效，应为asc或desc", "order")
            params['order'] = order
        
        return params
    
    @staticmethod
    def validate_fund_params() -> Dict[str, Any]:
        """验证基金查询参数"""
        params = {}
        
        # code 参数验证
        code = request.args.get('code', '').strip()
        if code:
            if not re.match(r'^[0-9]{6}$', code):
                raise ValidationError("基金代码格式无效，应为6位数字", "code")
            params['code'] = code
        
        # name 参数验证
        name = request.args.get('name', '').strip()
        if name:
            if len(name) > 100:
                raise ValidationError("基金名称长度不能超过100个字符", "name")
            params['name'] = name
        
        # type 参数验证
        fund_type = request.args.get('type', '').strip()
        if fund_type:
            valid_types = ['股票型', '债券型', '混合型', '货币型', 'QDII', 'ETF', 'LOF']
            if fund_type not in valid_types:
                raise ValidationError(f"基金类型无效，应为{', '.join(valid_types)}之一", "type")
            params['type'] = fund_type
        
        # status 参数验证
        status = request.args.get('status', '').strip()
        if status:
            if status not in ['L', 'D', 'S']:
                raise ValidationError("状态参数无效，应为L、D或S", "status")
            params['status'] = status
        
        # limit 参数验证
        limit_str = request.args.get('limit', '500')
        try:
            limit = int(limit_str)
            if limit <= 0:
                raise ValidationError("限制数量必须大于0", "limit")
            if limit > 1000:
                raise ValidationError("限制数量不能超过1000", "limit")
            params['limit'] = limit
        except ValueError:
            raise ValidationError("限制数量必须为有效整数", "limit")
        
        # order 参数验证
        order = request.args.get('order', '').lower().strip()
        if order:
            if order not in ['asc', 'desc']:
                raise ValidationError("排序参数无效，应为asc或desc", "order")
            params['order'] = order
        
        return params

class ResponseFormatter:
    """响应格式化器"""
    
    @staticmethod
    def success(data: Any, message: str = "操作成功", total: Optional[int] = None) -> Dict[str, Any]:
        """成功响应格式"""
        response = {
            "code": 200,
            "message": message,
            "data": data,
            "timestamp": int(__import__('time').time())
        }
        
        if total is not None:
            response["total"] = total
        
        if isinstance(data, list):
            response["count"] = len(data)
        
        return response
    
    @staticmethod
    def error(message: str, code: int = 400, field: str = None) -> Dict[str, Any]:
        """错误响应格式"""
        response = {
            "code": code,
            "message": message,
            "data": None,
            "timestamp": int(__import__('time').time())
        }
        
        if field:
            response["field"] = field
        
        return response
    
    @staticmethod
    def validation_error(error: ValidationError) -> Dict[str, Any]:
        """参数验证错误响应"""
        return ResponseFormatter.error(
            message=f"参数验证失败: {error.message}",
            code=400,
            field=error.field
        )
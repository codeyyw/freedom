import os
import psycopg2
import logging
from flask import Flask, jsonify, request

app = Flask(__name__)

# 配置日志，输出格式和级别按需调整
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def get_db_connection():
    return psycopg2.connect(
        host=os.environ.get('PG_HOST_OUT'),
        port=int(os.environ.get('PG_PORT', 5432)),
        user=os.environ.get('PG_USER'),
        password=os.environ.get('PG_PASSWORD'),
        dbname=os.environ.get('PG_DB')
    )


@app.route("/fundinfo", methods=["GET"])
def stockinfo_handler():
    rid = request.headers.get(os.environ.get('REQUEST_ID_HEADER'), '')
    # 打印请求基本信息
    logger.info(f"[RequestId: {rid}] Incoming request URL: {request.url}")
    logger.info(f"[RequestId: {rid}] Raw GET parameters: {dict(request.args)}")

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        conditions = []
        params = []

        # name 筛选（模糊匹配 cname 或 name，左模糊）
        name = request.args.get("name", "").strip()
        if name:
            conditions.append("(fund_name LIKE %s)")
            like_pattern = name + "%"
            params.extend([like_pattern, like_pattern])

        # fund_type 筛选（精确匹配）
        type = request.args.get("type", "").strip()
        if type:
            conditions.append("fund_type = %s")
            params.append(type)

        # fund_code 筛选（精确匹配）
        code = request.args.get("code", "").strip()
        if code:
            conditions.append("fund_code = %s")
            params.append(code)

        # status 筛选（精确匹配）
        status = request.args.get("status", "").strip()
        if status:
            conditions.append("status = %s")
            params.append(status)
        else:
            conditions.append("status = 'L'")

        # limit 参数
        try:
            limit = int(request.args.get("limit", 500))
        except ValueError:
            limit = 500
        if limit <= 0:
            limit = 500

        # 排序逻辑
        order = request.args.get("order", "").lower().strip()
        if order in ("asc", "desc"):
            order_clause = f" ORDER BY update_time {order.upper()}"
        else:
            order_clause = " ORDER BY fund_code ASC"

        # 构建 SQL
        sql = "SELECT * FROM fund_info"
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        sql += order_clause
        sql += " LIMIT %s"

        params.append(limit)

        logger.info(f"[RequestId: {rid}] Executing SQL: {sql}")
        logger.info(f"[RequestId: {rid}] SQL parameters: {params}")

        cur.execute(sql, params)

        colnames = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
        result = [dict(zip(colnames, row)) for row in rows]

        logger.info(f"[RequestId: {rid}] Query returned {len(result)} rows.")

        cur.close()
        conn.close()

        return jsonify(result)

    except Exception as e:
        logger.error(f"[RequestId: {rid}] Exception occurred: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000)

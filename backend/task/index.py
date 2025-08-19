import logging
import time
from datetime import datetime
from fundsync import sync_task_runner as fundsync_runner
from stocksync import sync_task_runner as stocksync_runner
from common.config import LOG_CONFIG

# 配置日志
logging.basicConfig(
    level=getattr(logging, LOG_CONFIG['level']),
    format=LOG_CONFIG['format'],
    datefmt=LOG_CONFIG['datefmt']
)
logger = logging.getLogger(__name__)

def run_fundsync_task():
    """运行基金同步任务"""
    logger.info("🎯 开始执行基金数据同步任务")
    
    try:
        result = fundsync_runner()
        if result:
            logger.info("✅ 基金数据同步任务完成")
            return result
        else:
            logger.error("❌ 基金数据同步任务失败")
            return {'success': False, 'error': '基金同步任务执行失败'}
    except Exception as e:
        logger.error(f"❌ 基金数据同步任务异常: {e}", exc_info=True)
        return {'success': False, 'error': str(e)}
    finally:
        logger.info("🏁 基金数据同步任务结束")

def run_stocksync_task():
    """运行股票同步任务"""
    logger.info("🎯 开始执行股票数据同步任务")
    
    try:
        result = stocksync_runner()
        if result:
            logger.info("✅ 股票数据同步任务完成")
            return result
        else:
            logger.error("❌ 股票数据同步任务失败")
            return {'success': False, 'error': '股票同步任务执行失败'}
    except Exception as e:
        logger.error(f"❌ 股票数据同步任务异常: {e}", exc_info=True)
        return {'success': False, 'error': str(e)}
    finally:
        logger.info("🏁 股票数据同步任务结束")

def main():
    """主函数：依次执行基金和股票同步任务"""
    start_time = time.time()
    
    logger.info(f"🎯 开始执行数据同步任务 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 执行结果统计
    results = {
        'fundsync': False,
        'stocksync': False
    }
    
    # 1. 先执行基金同步任务
    results['fundsync'] = run_fundsync_task()
    
    # 2. 再执行股票同步任务
    results['stocksync'] = run_stocksync_task()
    
    # 总结执行结果
    total_time = time.time() - start_time
    
    logger.info("📊 任务执行结果汇总:")
    
    # 详细显示每个任务的执行状态
    success_tasks = []
    failed_tasks = []
    
    for task_name, task_result in results.items():
        if isinstance(task_result, dict):
            if task_result['success']:
                logger.info(f"   {task_name}: ✅ 成功")
                success_tasks.append(task_name)
            else:
                logger.error(f"   {task_name}: ❌ 失败 - {task_result['error']}")
                failed_tasks.append(f"{task_name}({task_result['error']})")
        else:
            # 兼容旧的布尔返回值
            if task_result:
                logger.info(f"   {task_name}: ✅ 成功")
                success_tasks.append(task_name)
            else:
                logger.error(f"   {task_name}: ❌ 失败")
                failed_tasks.append(task_name)
    
    # 汇总统计
    logger.info(f"📈 成功任务: {len(success_tasks)} 个")
    if success_tasks:
        logger.info(f"   成功列表: {', '.join(success_tasks)}")
    
    logger.info(f"📉 失败任务: {len(failed_tasks)} 个")
    if failed_tasks:
        logger.error(f"   失败列表: {', '.join(failed_tasks)}")
    
    # 格式化总耗时
    if total_time >= 60:
        formatted_time = f"{total_time / 60:.2f} 分钟"
    else:
        formatted_time = f"{total_time:.2f} 秒"
    
    logger.info(f"⏱️  总耗时: {formatted_time}")
    logger.info(f"🎉 数据同步任务全部完成 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 返回执行状态
    success_count = len(success_tasks)
    if success_count == 2:
        return f"所有数据同步任务执行完毕。成功: {', '.join(success_tasks)}"
    elif success_count == 1:
        return f"部分数据同步任务执行失败。成功: {', '.join(success_tasks)}；失败: {', '.join(failed_tasks)}"
    else:
        return f"所有数据同步任务执行失败。失败原因: {', '.join(failed_tasks)}"

def handler(event, context):
    """AWS Lambda处理函数"""
    logger.warning("收到调用请求，开始执行数据同步任务...")
    result = main()
    logger.warning("数据同步任务完成，准备返回。")
    return result

if __name__ == "__main__":
    main()
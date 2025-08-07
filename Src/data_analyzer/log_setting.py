import logging
from pathlib import Path

def setup_logging(log_dir: str = "Logs", log_file: str = "app.log", level=logging.DEBUG):
    """
    配置日志系统
    :param log_dir: 日志目录
    :param log_file: 日志文件名
    :param level: 日志级别
    """
    logs_dir = Path(log_dir)
    logs_dir.mkdir(exist_ok=True)

    log_path = logs_dir / log_file

    # 避免重复添加 handler
    if not logging.getLogger().hasHandlers():
        logging.basicConfig(
            filename=log_path,
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            encoding='utf-8'  # 防止中文乱码
        )

    # 返回一个命名的 logger（推荐使用模块名）
    return logging.getLogger(__name__)
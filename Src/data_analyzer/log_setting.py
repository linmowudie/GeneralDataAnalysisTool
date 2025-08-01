import logging
from pathlib import Path

def setup_logging():
    logs_dir = Path('Logs')
    logs_dir.mkdir(exist_ok=True)

    log_file = logs_dir / 'app.log'

    logging.basicConfig(
        filename=log_file,
        level=logging.ERROR,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
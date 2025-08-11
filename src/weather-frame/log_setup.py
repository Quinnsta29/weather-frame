import json
import logging
import logging.config
from pathlib import Path
from typing_extensions import override

BASE_DIR = Path(__file__).resolve().parent
config_path = Path(BASE_DIR / 'config' / 'logging_config.json')
error_logs_path = Path(BASE_DIR / 'logs' / 'error_logs')

def setup_logging(logger_name: str, config_path=config_path) -> None:
    """Setup logging configuration and create """
    if not config_path.exists():
        raise FileNotFoundError(f"Logging configuration file not found: {config_path}")

    with open(config_path, 'r') as config_file:
        config = json.load(config_file)

    logging.config.dictConfig(config)
    return logging.getLogger(logger_name)
    
logger: logging.Logger = setup_logging('weather_frame_logger')

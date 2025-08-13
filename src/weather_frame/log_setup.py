import json
import logging
import logging.config

from weather_frame.config import CONFIG_PATH

def setup_logging(logger_name: str, config_path=CONFIG_PATH) -> None:
    """Setup logging configuration and create """
    if not config_path.exists():
        raise FileNotFoundError(f"Logging configuration file not found: {config_path}")

    with open(config_path, 'r') as config_file:
        config = json.load(config_file)

    logging.config.dictConfig(config)
    return logging.getLogger(logger_name)
    
logger: logging.Logger = setup_logging('weather_frame_logger')

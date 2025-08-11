import json
import logging
import logging.config
from pathlib import Path
# from typing import Any, override
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

    if not error_logs_path.exists():
        error_logs_path.mkdir(parents=True)

    config['handlers']['to_json']['filename'] = str(error_logs_path / 'error_logs.jsonl')

    logging.config.dictConfig(config)
    return logging.getLogger(logger_name)

class MyJSONFormatter(logging.Formatter):
    """Custom JSON formatter for logging."""
    def __init__(
            self,
            *,
            fmt_keys: dict[str, str] = None,
    ):
        super().__init__()
        self.fmt_keys = fmt_keys if fmt_keys is not None else {}

    @override
    def format(self, record: logging.LogRecord) -> str:
        message = self._prepare_log_dict(record)
        return json.dumps(message, default=str)
    
    def _prepare_log_dict(self, record: logging.LogRecord):
        """Prepare a dictionary for logging."""
        message = {
            'timestamp': self.formatTime(record, self.datefmt),
            'message': record.getMessage(),
            'logger': record.name,
        }

        for key, value in self.fmt_keys.items():
            if hasattr(record, value):
                message[key] = getattr(record, value)
        return message
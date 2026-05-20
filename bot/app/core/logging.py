import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging(debug: bool = False, neural_api_error_log_path: str = "logs/neural_api_errors.log") -> None:
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    neural_log_path = Path(neural_api_error_log_path)
    neural_log_path.parent.mkdir(parents=True, exist_ok=True)

    neural_logger = logging.getLogger("app.services.neural_api")
    neural_logger.setLevel(logging.WARNING)
    neural_logger.propagate = False

    if not any(
        isinstance(handler, RotatingFileHandler)
        and Path(handler.baseFilename) == neural_log_path.resolve()
        for handler in neural_logger.handlers
    ):
        file_handler = RotatingFileHandler(
            neural_log_path,
            maxBytes=2_000_000,
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setLevel(logging.WARNING)
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")
        )
        neural_logger.addHandler(file_handler)

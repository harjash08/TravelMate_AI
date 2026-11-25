import logging
import sys
import time
from functools import wraps
from pathlib import Path
from inspect import iscoroutinefunction

# Create logs directory
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# Centralized logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(
            LOG_DIR / "travel_agent.log",
            encoding="utf-8"
        )
    ],
    force=True
)


def get_logger(name):
    return logging.getLogger(name)


def track_execution(func):

    logger = get_logger(func.__module__)

    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        start = time.perf_counter()
        logger.info("STARTED: %s", func.__name__)

        try:
            result = await func(*args, **kwargs)
            logger.info("COMPLETED: %s", func.__name__)
            return result

        except Exception:
            logger.exception("FAILED: %s", func.__name__)
            raise

        finally:
            logger.info(
                "TIME TAKEN: %s | %.2f seconds",
                func.__name__,
                time.perf_counter() - start
            )

    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        start = time.perf_counter()
        logger.info("STARTED: %s", func.__name__)

        try:
            result = func(*args, **kwargs)
            logger.info("COMPLETED: %s", func.__name__)
            return result

        except Exception:
            logger.exception("FAILED: %s", func.__name__)
            raise

        finally:
            logger.info(
                "TIME TAKEN: %s | %.2f seconds",
                func.__name__,
                time.perf_counter() - start
            )

    return async_wrapper if iscoroutinefunction(func) else sync_wrapper

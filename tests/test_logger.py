import logging
from core.logger import get_logger

def test_logger_creation():
    logger = get_logger("swingdesk")
    assert isinstance(logger, logging.Logger)
    assert logger.name == "swingdesk"

def test_logging_no_exception():
    logger = get_logger("swingdesk")
    try:
        logger.info("Test logging output")
    except Exception as e:
        assert False, f"Proses logging menghasilkan exception: {e}"

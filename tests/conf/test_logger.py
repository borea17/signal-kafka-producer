import logging

from signalation.conf.logger import get_logger

logger = get_logger(__file__)


def test_logger_works_as_expected(caplog):
    assert type(logger) == logging.Logger
    test_logging_message = "this is a test"
    logger.info(test_logging_message)
    assert test_logging_message in caplog.text

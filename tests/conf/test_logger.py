from signalation.conf.logger import get_logger


def test_logger_works_as_expected(caplog):
    name_of_logger = "signalation.test_logger"
    logger = get_logger(name_of_logger)
    test_logging_message = "this is a test"
    logger.info(test_logging_message)
    assert test_logging_message in caplog.text

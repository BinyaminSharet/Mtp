import logging
import unittest


test_logger = None


def get_test_logger():
    global test_logger
    if test_logger is None:
        logger = logging.getLogger('unit_test_logs')
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] -> %(message)s'
        )
        handler = logging.FileHandler('logs/test.log', mode='w')
        handler.setFormatter(formatter)
        handler.setLevel(logging.DEBUG)
        logger.addHandler(handler)
        test_logger = logger
    return test_logger


class BaseTestCase(unittest.TestCase):

    def setUp(self):
        self.logger = get_test_logger()
        self.logger.debug('TESTING METHOD: %s', self._testMethodName)

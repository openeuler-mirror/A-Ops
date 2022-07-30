import unittest
from unittest.mock import Mock

from aops_check.errors.startup_error import StartupError


class StartupErrorTestCase(unittest.TestCase):
    def test_get_check_mode_property(self):
        check_mode = Mock()
        error = StartupError(check_mode, Mock())
        self.assertEqual(error.check_mode, check_mode)

    def test_get_support_mode_property(self):
        support_mode = [Mock(), Mock()]
        error = StartupError(Mock(), support_mode)
        self.assertEqual(error.support_mode, support_mode)

    def test_str_should_return_correct_result(self):
        check_mode = "a"
        support_mode = ["b", "c"]
        error = StartupError(check_mode, support_mode)
        self.assertEqual(str(error), f"Check module's mode should be in ['b', 'c'], not a")

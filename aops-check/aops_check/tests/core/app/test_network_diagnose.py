import unittest
from unittest import mock
from unittest.mock import Mock

from aops_check.core.experiment.app.network_diagnose import NetworkDiagnoseApp


# abnormal
class SingleModel1:
    @staticmethod
    def calculate(data):
        return [1]


# normal
class SingleModel2:
    @staticmethod
    def calculate(data):
        return []


# abnormal
class MultiModel1:
    @staticmethod
    def calculate(data):
        return True


# normal
class MultiModel2:
    @staticmethod
    def calculate(data):
        return False


class NetworkDiagnoseTestCase(unittest.TestCase):
    def test_do_single_check_should_return_correct_value_when_input_is_normal(self):
        detail = {
            "host1": {
                "metric1": "model1",
                "metric2": "model2"
            }
        }
        data = {
            "host1": {
                "metric1{l1=1}": [[1, 1], [2, 3]],
                "metric2{l2=2}": [[1, 1]]
            }
        }
        app = NetworkDiagnoseApp()
        app.model = {'model1': SingleModel1, 'model2': SingleModel2}
        self.assertEqual(app.do_single_check(detail, data),
                         {'host1': [{"metric_name": "metric1", "metric_label": "{l1=1}"}]})

    def test_do_single_check_should_return_empty_when_metrics_is_none(self):
        detail = {
            "host1": {
                "metric1": "model1",
                "metric2": "model2"
            }
        }
        data = {
            "host1": {
                "metric1{l1=1}": None,
                "metric2{l2=1}": []
            },
            "host2": None
        }
        app = NetworkDiagnoseApp()
        app.model = {'model1': SingleModel1, 'model2': SingleModel2}
        self.assertEqual(app.do_single_check(detail, data), {})

    def test_do_multi_check_should_return_correct_value_when_input_is_normal(self):
        detail = {
            "host1": "model1",
            "host2": "model2"
        }
        data = {
            "host1": [{"metric_name": "metric1"}],
            "host2": [{"metric_name": "metric2"}, {"metric_name": "metric3"}]
        }
        app = NetworkDiagnoseApp()
        app.model = {"model1": MultiModel1, "model2": MultiModel2}
        self.assertEqual(app.do_multi_check(detail, data), {"host1": [{"metric_name": "metric1"}]})

    def test_do_multi_check_should_return_all_when_detail_is_not_matched(self):
        detail = {
            "host1": "model3",
            "host3": "model2"
        }
        data = {
            "host1": [{"metric_name": "metric1"}],
            "host2": [{"metric_name": "metric2"}, {"metric_name": "metric3"}]
        }
        app = NetworkDiagnoseApp()
        app.model = {"model1": MultiModel1, "model2": MultiModel2}
        self.assertEqual(app.do_multi_check(detail, data), {
            "host1": [{"metric_name": "metric1"}],
            "host2": [{"metric_name": "metric2"}, {"metric_name": "metric3"}]
        })

    def test_do_diag_should_return_empty_when_model_is_none(self):
        detail = "11"
        app = NetworkDiagnoseApp()
        self.assertEqual(app.do_diag(detail, 1), ("", "", ""))

    def test_format_result_should_return_correct_value_when_is_normal(self):
        multi_check_result = {
            "host1": [{"metric_name": "m1", "metric_label": "l1"}, {"metric_name": "m2", "metric_label": "l2"},
                      {"metric_name": "m3", "metric_label": "l3"}],
            "host2": [{"metric_name": "m1", "metric_label": "l1"}, {"metric_name": "m2", "metric_label": "l2"}]
        }
        diag_result = "host1", "m2", "l2"
        expect_result = {
            "host1": [{"metric_name": "m1", "metric_label": "l1", "is_root": False},
                      {"metric_name": "m2", "metric_label": "l2", "is_root": True},
                      {"metric_name": "m3", "metric_label": "l3", "is_root": False}],
            "host2": [{"metric_name": "m1", "metric_label": "l1", "is_root": False},
                      {"metric_name": "m2", "metric_label": "l2", "is_root": False}]
        }
        app = NetworkDiagnoseApp()
        self.assertEqual(app.format_result(multi_check_result, diag_result), expect_result)

    @mock.patch.object(NetworkDiagnoseApp, 'load_models')
    def test_execute_should_return_empty_when_load_models_fail(self, mock_load_models):
        app = NetworkDiagnoseApp()
        fake_model_info = Mock()
        fake_detail = Mock()
        fake_data = Mock()
        fake_load_models = False
        mock_load_models.return_value = fake_load_models
        self.assertEqual(app.execute(fake_model_info, fake_detail, fake_data), {})
        mock_load_models.assert_called_once_with(fake_model_info)

    @mock.patch.object(NetworkDiagnoseApp, 'do_single_check')
    @mock.patch.object(NetworkDiagnoseApp, 'load_models')
    def test_execute_should_return_empty_when_return_no_single_check_result(self, mock_load_models,
                                                                            mock_do_single_check):
        app = NetworkDiagnoseApp()
        fake_model_info = Mock()
        fake_detail = {
            "singlecheck": Mock()
        }
        fake_data = Mock()
        fake_load_models = True
        mock_load_models.return_value = fake_load_models
        mock_do_single_check.return_value = {}
        self.assertEqual(app.execute(fake_model_info, fake_detail, fake_data), {})
        mock_do_single_check.assert_called_once_with(fake_detail['singlecheck'], fake_data)

    @mock.patch.object(NetworkDiagnoseApp, 'do_multi_check')
    @mock.patch.object(NetworkDiagnoseApp, 'do_single_check')
    @mock.patch.object(NetworkDiagnoseApp, 'load_models')
    def test_execute_should_return_empty_when_return_no_multi_check_result(self, mock_load_models,
                                                                           mock_do_single_check,
                                                                           mock_do_multi_check):
        app = NetworkDiagnoseApp()
        fake_model_info = Mock()
        fake_detail = {
            "singlecheck": Mock(),
            "multicheck": Mock()
        }
        fake_data = Mock()
        fake_load_models = True
        fake_single_check_result = Mock()
        mock_load_models.return_value = fake_load_models
        mock_do_single_check.return_value = fake_single_check_result
        mock_do_multi_check.return_value = {}
        self.assertEqual(app.execute(fake_model_info, fake_detail, fake_data), {})
        mock_do_multi_check.assert_called_once_with(fake_detail['multicheck'], fake_single_check_result)

    @mock.patch.object(NetworkDiagnoseApp, 'format_result')
    @mock.patch.object(NetworkDiagnoseApp, 'do_diag')
    @mock.patch.object(NetworkDiagnoseApp, 'do_multi_check')
    @mock.patch.object(NetworkDiagnoseApp, 'do_single_check')
    @mock.patch.object(NetworkDiagnoseApp, 'load_models')
    def test_execute_should_have_correct_steps(self, mock_load_models,
                                               mock_do_single_check,
                                               mock_do_multi_check,
                                               mock_do_diag,
                                               mock_format_result):
        app = NetworkDiagnoseApp()
        fake_model_info = Mock()
        fake_detail = {
            "singlecheck": Mock(),
            "multicheck": Mock(),
            "diag": Mock()
        }
        fake_data = Mock()
        fake_load_models = True
        fake_single_check_result = Mock()
        fake_multi_check_result = Mock()
        fake_diag_result = Mock()
        mock_load_models.return_value = fake_load_models
        mock_do_single_check.return_value = fake_single_check_result
        mock_do_multi_check.return_value = fake_multi_check_result
        mock_do_diag.return_value = fake_diag_result

        app.execute(fake_model_info, fake_detail, fake_data)
        mock_load_models.assert_called_once_with(fake_model_info)
        mock_do_single_check.assert_called_once_with(fake_detail['singlecheck'], fake_data)
        mock_do_multi_check.assert_called_once_with(fake_detail['multicheck'], fake_single_check_result)
        mock_do_diag.assert_called_once_with(fake_detail['diag'], fake_multi_check_result)
        mock_format_result.assert_called_once_with(fake_multi_check_result, fake_diag_result)


if __name__ == '__main__':
    unittest.main()

import unittest
from unittest import mock

from aops_check.core.experiment.algorithm.diag.statistic_diag import StatisticDiag


class StatisticDiagTestcase(unittest.TestCase):

    def test_run_should_return_correct_result_when_input_is_normal(self):
        ...

    def test_get_candidate_should_return_correct_result_when_input_is_larger_than_k(self):
        data = {
            "1": [1, 2, 3, 4],
            "2": [2, 3, 4],
            "3": [1, 2, 2, 1, 1],
            "4": [1, 2, 2],
            "5": [1, 2, 2, 2, 2, 2]
        }
        diag = StatisticDiag(2)
        result = diag.get_candidate(data)
        self.assertEqual(result, ["3", "5"])

    def test_get_candidate_should_return_all_id_when_input_is_smaller_than_k(self):
        data = {
            "1": [1, 2, 3, 4],
            "2": [2, 3, 4],
            "3": [1, 2, 2, 1, 1],
            "4": [1, 2, 2],
            "5": [1, 2, 2, 2, 2, 2]
        }
        diag = StatisticDiag(6)
        result = diag.get_candidate(data)
        self.assertEqual(result, ["1", "2", "3", "4", "5"])

    def test_count_fault_score_should_return_correct_value_when_map_is_matched(self):
        failure_info = [{'name': 'cpu'}, {'name': 'mem'}]
        score_map = {'cpu': 1, 'mem': 0.2}
        diag = StatisticDiag()
        self.assertEqual(diag.count_fault_score(failure_info, score_map), 1.2)

    def test_count_fault_score_should_return_correct_value_when_map_is_not_matched(self):
        failure_info = [{'name': 'cpu'}, {'name': 'mem'}]
        score_map = {'cpu': 1, 'ss': 0.2}
        diag = StatisticDiag()
        self.assertEqual(diag.count_fault_score(failure_info, score_map), 1.5)

    @mock.patch.object(StatisticDiag, 'count_fault_score')
    def test_get_root_should_return_max_score_root_when_input_is_normal(self, mock_count):
        mock_count.side_effect = [1, 3, 2]
        candidate = ['1', '2', '3']
        check_result = {'1': 1, "2": 2, "3": 3}
        diag = StatisticDiag()
        self.assertEqual(diag.get_root(candidate, check_result), '2')


if __name__ == '__main__':
    unittest.main()

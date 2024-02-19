import unittest
from unittest.mock import patch, PropertyMock
from round_robin_api.round_robin import get_instances, get_next_instance, Status, app, MAX_RETRY, make_request_and_update_status, APPLICATION_TIMEOUT
from flask import jsonify

class TestRoundRobin(unittest.TestCase):
    def setUp(self):
        self.application_instances = [
            "http://localhost:5001",
            "http://localhost:5002",
            "http://localhost:5003"
        ]
        self.instance_status = {
            "http://localhost:5001": Status.HEALTHY,
            "http://localhost:5002": Status.SLOW,
            "http://localhost:5003": Status.DOWN
        }


    @patch('round_robin_api.round_robin.application_instances', new_callable=list)
    @patch('round_robin_api.round_robin.instance_status', new_callable=dict)
    def test_get_instances_healthy(self, mock_status, mock_instances):
        mock_instances[:] = self.application_instances
        mock_status.update(self.instance_status)
        expected_instance = "http://localhost:5001"

        actual_instance = get_instances(Status.HEALTHY)

        self.assertEqual(actual_instance, expected_instance)



    @patch('round_robin_api.round_robin.application_instances', new_callable=list)
    @patch('round_robin_api.round_robin.instance_status', new_callable=dict)
    def test_get_instances_slow(self, mock_status, mock_instances):
        # Arrange
        mock_instances[:] = self.application_instances
        mock_status.update(self.instance_status)
        expected_instance = "http://localhost:5002"

        actual_instance = get_instances(Status.SLOW)

        self.assertEqual(actual_instance, expected_instance)


    @patch('round_robin_api.round_robin.application_instances', new_callable=list)
    @patch('round_robin_api.round_robin.instance_status', new_callable=dict)
    def test_get_instances_down(self, mock_status, mock_instances):
        mock_instances[:] = self.application_instances
        mock_status.update(self.instance_status)
        expected_instance = "http://localhost:5003"

        actual_instance = get_instances(Status.DOWN)

        self.assertEqual(actual_instance, expected_instance)


    @patch('round_robin_api.round_robin.application_instances', new_callable=list)
    @patch('round_robin_api.round_robin.instance_status', new_callable=dict)
    @patch('round_robin_api.round_robin.instance_index', new_callable=int)
    def test_get_next_instance_healthy_round_robin(self, mock_index, mock_status, mock_instances):
        mock_instances[:] = [
            "http://localhost:5001",
            "http://localhost:5002",
            "http://localhost:5003",
            "http://localhost:5004"
        ]
        mock_status.update({
            "http://localhost:5001": Status.HEALTHY,
            "http://localhost:5002": Status.HEALTHY,
            "http://localhost:5003": Status.HEALTHY,
            "http://localhost:5004": Status.HEALTHY
        })
        mock_index = 0
        expected_instances = [
            "http://localhost:5001",
            "http://localhost:5002",
            "http://localhost:5003",
            "http://localhost:5004"
        ]

        for expected_instance in expected_instances:
            actual_instance = get_next_instance()
            self.assertEqual(actual_instance, expected_instance)

        actual_instance = get_next_instance()
        self.assertEqual(actual_instance, "http://localhost:5001")
    
if __name__ == '__main__':
    unittest.main()
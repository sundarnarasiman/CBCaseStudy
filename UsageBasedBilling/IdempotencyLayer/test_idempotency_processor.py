import unittest
from unittest.mock import patch, MagicMock
from idempotency_processor import IdempotencyProcessor

class TestIdempotencyProcessor(unittest.TestCase):

    @patch('idempotency_processor.Consumer')
    @patch('idempotency_processor.Producer')
    @patch('idempotency_processor.redis.Redis')
    def setUp(self, mock_redis, mock_producer, mock_consumer):
        self.mock_redis_instance = mock_redis.return_value
        self.processor = IdempotencyProcessor()

    def test_process_event_new(self):
        self.mock_redis_instance.setnx.return_value = 1
        event = {"idempotencyKey": "k1", "customerId": "c1"}
        
        with patch.object(self.processor, 'forward_event', return_value=True) as mock_forward:
            result = self.processor.process_event(event)
            self.assertTrue(result)
            mock_forward.assert_called_once_with(event)

    def test_process_event_duplicate(self):
        self.mock_redis_instance.setnx.return_value = 0
        event = {"idempotencyKey": "k1", "customerId": "c1"}
        
        with patch.object(self.processor, 'forward_event') as mock_forward:
            result = self.processor.process_event(event)
            self.assertFalse(result)
            mock_forward.assert_not_called()

if __name__ == '__main__':
    unittest.main()

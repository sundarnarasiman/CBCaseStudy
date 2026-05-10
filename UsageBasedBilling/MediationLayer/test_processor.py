import unittest
from unittest.mock import MagicMock, patch
from processor import MediationProcessor

class TestMediationProcessor(unittest.TestCase):

    @patch('processor.Consumer')
    @patch('processor.redis.Redis')
    def setUp(self, mock_redis, mock_consumer):
        self.mock_redis_instance = mock_redis.return_value
        self.processor = MediationProcessor()

    def test_deduplication_new_event(self):
        # SETNX returns 1 for a new key
        self.mock_redis_instance.setnx.return_value = 1
        
        is_duplicate = self.processor.deduplicate("test_key_123")
        self.assertFalse(is_duplicate)
        self.mock_redis_instance.setnx.assert_called_with("dedupe:test_key_123", "1")
        self.mock_redis_instance.expire.assert_called_with("dedupe:test_key_123", 86400)

    def test_deduplication_existing_event(self):
        # SETNX returns 0 if key already exists
        self.mock_redis_instance.setnx.return_value = 0
        
        is_duplicate = self.processor.deduplicate("test_key_123")
        self.assertTrue(is_duplicate)

    def test_update_counter(self):
        self.mock_redis_instance.incr.return_value = 5
        
        count = self.processor.update_counter("cust_1", "api_call")
        self.assertEqual(count, 5)
        self.mock_redis_instance.incr.assert_called_with("meter:cust_1:api_call")

    def test_process_event_valid(self):
        self.mock_redis_instance.setnx.return_value = 1 # Not a duplicate
        
        event = {
            "customerId": "cust_1",
            "event": "api_call",
            "idempotencyKey": "key_1"
        }
        
        self.processor.process_event(event)
        self.mock_redis_instance.incr.assert_called_with("meter:cust_1:api_call")

    def test_process_event_duplicate(self):
        self.mock_redis_instance.setnx.return_value = 0 # Duplicate
        
        event = {
            "customerId": "cust_1",
            "event": "api_call",
            "idempotencyKey": "key_1"
        }
        
        self.processor.process_event(event)
        # Should not increment counter
        self.mock_redis_instance.incr.assert_not_called()

if __name__ == '__main__':
    unittest.main()

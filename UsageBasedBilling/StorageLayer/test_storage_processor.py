import unittest
from unittest.mock import patch, MagicMock
from storage_processor import StorageProcessor

class TestStorageProcessor(unittest.TestCase):

    @patch('storage_processor.Consumer')
    @patch('storage_processor.boto3.client')
    @patch('storage_processor.Client')
    def setUp(self, mock_ch, mock_boto, mock_consumer):
        self.mock_s3 = mock_boto.return_value
        self.mock_ch_instance = mock_ch.return_value
        self.processor = StorageProcessor()

    def test_save_raw_to_s3(self):
        event = {
            "idempotencyKey": "key_123",
            "customerId": "cust_1",
            "event": "api_call"
        }
        result = self.processor.save_raw_to_s3(event)
        self.assertTrue(result)
        self.mock_s3.put_object.assert_called_once()

    def test_save_aggregate_to_clickhouse(self):
        event = {
            "idempotencyKey": "key_123",
            "customerId": "cust_1",
            "event": "api_call",
            "timestamp": "2026-05-10T12:00:00Z"
        }
        result = self.processor.save_aggregate_to_clickhouse(event)
        self.assertTrue(result)
        self.mock_ch_instance.execute.assert_called()

    def test_process_event_calls_both_storage(self):
        event = {
            "idempotencyKey": "key_123",
            "customerId": "cust_1",
            "event": "api_call",
            "timestamp": "2026-05-10T12:00:00Z"
        }
        
        with patch.object(self.processor, 'save_raw_to_s3') as mock_s3_save:
            with patch.object(self.processor, 'save_aggregate_to_clickhouse') as mock_ch_save:
                self.processor.process_event(event)
                mock_s3_save.assert_called_once_with(event)
                mock_ch_save.assert_called_once_with(event)

if __name__ == '__main__':
    unittest.main()

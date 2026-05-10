import unittest
from unittest.mock import patch, MagicMock
from rating_processor import RatingProcessor

class TestRatingProcessor(unittest.TestCase):

    @patch('rating_processor.Consumer')
    @patch('rating_processor.boto3.client')
    @patch('rating_processor.Client')
    def setUp(self, mock_ch, mock_boto, mock_consumer):
        self.mock_ch_instance = mock_ch.return_value
        self.mock_s3 = mock_boto.return_value
        self.processor = RatingProcessor()

    def test_fetch_usage(self):
        self.mock_ch_instance.execute.return_value = [('api_call', 1000), ('storage_gb', 50)]
        
        result = self.processor.fetch_usage('cust_1', '2026-05-01', '2026-05-31')
        self.assertEqual(len(result), 2)
        self.mock_ch_instance.execute.assert_called_once()

    def test_calculate_charges(self):
        usage_data = [('api_call', 1000), ('storage_gb', 50)]
        # 1000 * 0.01 = 10.0, 50 * 0.05 = 2.5. Total = 12.5
        line_items, total = self.processor.calculate_charges(usage_data)
        
        self.assertEqual(total, 12.5)
        self.assertEqual(len(line_items), 2)
        self.assertEqual(line_items[0]['amount'], 10.0)

    def test_generate_and_save_invoice(self):
        line_items = [{'event_type': 'api_call', 'amount': 10.0}]
        
        invoice = self.processor.generate_and_save_invoice('cust_1', line_items, 10.0, '2026-05')
        self.assertIsNotNone(invoice)
        self.assertEqual(invoice['total_amount'], 10.0)
        self.mock_s3.put_object.assert_called_once()

    def test_process_trigger(self):
        trigger = {
            "customerId": "cust_1",
            "startDate": "2026-05-01",
            "endDate": "2026-05-31"
        }
        
        self.mock_ch_instance.execute.return_value = [('api_call', 1000)]
        
        with patch.object(self.processor, 'generate_and_save_invoice') as mock_save:
            self.processor.process_trigger(trigger)
            mock_save.assert_called_once()

if __name__ == '__main__':
    unittest.main()

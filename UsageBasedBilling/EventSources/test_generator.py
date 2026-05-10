import unittest
from generator import generate_event

class TestEventGenerator(unittest.TestCase):
    def test_generate_event(self):
        event = generate_event()
        self.assertIn("customerId", event)
        self.assertIn("event", event)
        self.assertIn("timestamp", event)
        self.assertIn("idempotencyKey", event)

if __name__ == '__main__':
    unittest.main()

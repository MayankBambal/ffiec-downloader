import unittest
from ffiec_call_reports import FFIECClient

class TestFFIECClient(unittest.TestCase):
    def setUp(self):
        self.client = FFIECClient(
            username="test_user",
            passphrase="test_pass"
        )
    
    def test_initialization(self):
        self.assertEqual(self.client.username, "test_user")
        self.assertEqual(self.client.passphrase, "test_pass")
        self.assertIsNotNone(self.client.headers)

if __name__ == '__main__':
    unittest.main() 
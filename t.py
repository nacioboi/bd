import unittest
import json

# Mock-up of your Packet class based on what I understand
class Packet:
    def __init__(self, json_str):
        self.data = json.loads(json_str)

    @classmethod
    def encode(cls, **kwargs):
        json_str = json.dumps(kwargs)
        return cls(json_str)

# Actual Test Class
class TestPacket(unittest.TestCase):

    def test_encode_and_init(self):
        # Create a Packet instance using the encode class method
        packet_instance = Packet.encode(type='handshake', encoding='utf-8', buffer_size=1, suffix='\x03', split_char='\x00')
        
        # Verify if the Packet instance has correctly stored the data
        self.assertEqual(packet_instance.data, {
            'type': 'handshake',
            'encoding': 'utf-8',
            'buffer_size': 1,
            'suffix': '\x03',
            'split_char': '\x00'
        })

    def test_json_decode_error(self):
        # Test a JSONDecodeError
        with self.assertRaises(json.JSONDecodeError):
            Packet("{type: handshake}")  # Missing quotes around keys

if __name__ == "__main__":
    unittest.main()


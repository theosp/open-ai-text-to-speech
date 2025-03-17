import unittest
from app import app

class FlaskAppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
    
    def test_home_page(self):
        """Test that the home page loads correctly"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Text-to-Speech Generator', response.data)
    
    def test_history_page(self):
        """Test that the history page loads correctly"""
        response = self.app.get('/history')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Generation History', response.data)
    
    def test_preview_endpoint(self):
        """Test that the preview endpoint works correctly"""
        response = self.app.post('/preview', data={
            'text': 'Test text',
            'model': 'tts-1'
        })
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertIn('text_length', json_data)
        self.assertIn('num_chunks', json_data)
        self.assertIn('cost', json_data)

if __name__ == '__main__':
    unittest.main() 
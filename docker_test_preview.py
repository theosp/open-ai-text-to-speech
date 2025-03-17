import io
import os
import json
from app import app
from werkzeug.datastructures import FileStorage

def test_preview():
    """Test the preview endpoint directly using Flask's test client"""
    try:
        # Open the PDF file
        with open("test.pdf", "rb") as f:
            pdf_content = f.read()
        
        print(f"PDF content length: {len(pdf_content)}")
        
        # Create a test client
        client = app.test_client()
        
        # Disable CSRF for testing
        app.config['WTF_CSRF_ENABLED'] = False
        
        # Create a FileStorage object
        pdf_file = FileStorage(
            stream=io.BytesIO(pdf_content),
            filename="test.pdf",
            content_type="application/pdf",
        )
        
        # Create a test request with the PDF file
        data = {'model': 'tts-1'}
        files = {'pdf_file': pdf_file}
        
        # Create a test request with the PDF file
        response = client.post(
            '/preview',
            data=data,
            content_type='multipart/form-data',
            buffered=True
        )
        
        # Print the response
        print(f"Response status: {response.status_code}")
        print(f"Response data: {response.data}")
        
        # Parse the JSON response
        try:
            data = json.loads(response.data)
            print(f"Parsed response: {data}")
        except:
            print("Could not parse response as JSON")
        
        return response
    except Exception as e:
        print(f"Error testing preview: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_preview() 
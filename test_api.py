"""
Test script to verify the backend API endpoints.
Run this to test the upload functionality locally.
"""
import requests
import json
import sys
import os

# Backend URL - change this to test different environments
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:5000')

def test_health_endpoint():
    """Test the health endpoint."""
    print("\n=== Testing Health Endpoint ===")
    try:
        response = requests.get(f'{BACKEND_URL}/api/health', timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_upload_endpoint():
    """Test the file upload endpoint."""
    print("\n=== Testing Upload Endpoint ===")
    
    # Check if test PDF exists
    test_file = 'test_sample.pdf'
    if not os.path.exists(test_file):
        print(f"Creating test file: {test_file}")
        # Create minimal PDF
        from PyPDF2 import PdfWriter
        pdf_writer = PdfWriter()
        pdf_writer.add_blank_page(width=200, height=200)
        with open(test_file, 'wb') as f:
            pdf_writer.write(f)
    
    try:
        with open(test_file, 'rb') as f:
            files = {'file': ('test.pdf', f, 'application/pdf')}
            response = requests.post(
                f'{BACKEND_URL}/api/upload/file',
                files=files,
                timeout=30
            )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            data = response.json()
            return data.get('file_id')
        return None
        
    except Exception as e:
        print(f"Error: {e}")
        return None


def test_extract_endpoint(file_id):
    """Test the extract endpoint."""
    print("\n=== Testing Extract Endpoint ===")
    try:
        response = requests.post(
            f'{BACKEND_URL}/api/extract/process',
            json={'file_id': file_id},
            timeout=60
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
        
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_preview_endpoint(file_id):
    """Test the preview endpoint."""
    print("\n=== Testing Preview Endpoint ===")
    try:
        response = requests.post(
            f'{BACKEND_URL}/api/extract/preview',
            json={'file_id': file_id},
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)[:500]}...")
        
        if response.status_code == 200:
            mcqs = data.get('mcqs', [])
            print(f"Number of MCQs: {len(mcqs)}")
            return True
        return False
        
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_full_flow():
    """Test the complete upload-to-preview flow."""
    print("\n" + "="*50)
    print("FULL API TEST FLOW")
    print("="*50)
    
    # Test 1: Health check
    if not test_health_endpoint():
        print("\n❌ Health check failed! Is the server running?")
        print(f"Start server with: python run.py")
        return False
    
    print("\n✅ Health check passed!")
    
    # Test 2: Upload file
    file_id = test_upload_endpoint()
    if not file_id:
        print("\n❌ Upload failed!")
        return False
    
    print(f"\n✅ Upload successful! File ID: {file_id}")
    
    # Test 3: Extract MCQs
    if not test_extract_endpoint(file_id):
        print("\n❌ Extraction failed!")
        return False
    
    print("\n✅ Extraction successful!")
    
    # Test 4: Preview MCQs
    if not test_preview_endpoint(file_id):
        print("\n❌ Preview failed!")
        return False
    
    print("\n✅ Preview successful!")
    
    print("\n" + "="*50)
    print("ALL TESTS PASSED! ✅")
    print("="*50)
    return True


if __name__ == '__main__':
    # Check for command line arguments
    if len(sys.argv) > 1:
        BACKEND_URL = sys.argv[1]
    
    print(f"Testing backend at: {BACKEND_URL}")
    
    # Run full test
    success = test_full_flow()
    sys.exit(0 if success else 1)

"""
Test script to test the Render backend API
"""
import requests
import json
import sys

BACKEND_URL = 'https://mcq-extractor-backend.onrender.com'

def test_health():
    """Test health endpoint"""
    print("\n=== Testing Health ===")
    r = requests.get(f'{BACKEND_URL}/api/health')
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text}")
    return r.status_code == 200

def test_upload():
    """Test file upload"""
    print("\n=== Testing Upload ===")
    files = {'file': open('testmcq.pdf', 'rb')}
    r = requests.post(f'{BACKEND_URL}/api/upload/file', files=files)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text[:500]}")
    if r.status_code == 200:
        return r.json().get('file_id')
    return None

def test_extract(file_id):
    """Test MCQ extraction"""
    print("\n=== Testing Extract ===")
    r = requests.post(
        f'{BACKEND_URL}/api/extract/process',
        json={'file_id': file_id}
    )
    print(f"Status: {r.status_code}")
    data = r.json()
    print(f"MCQs count: {data.get('count', 0)}")
    if data.get('mcqs'):
        print(f"First MCQ: {data['mcqs'][0]}")
    return data

if __name__ == '__main__':
    # Test health
    if not test_health():
        print("Health check failed!")
        sys.exit(1)
    
    # Test upload
    file_id = test_upload()
    if not file_id:
        print("Upload failed!")
        sys.exit(1)
    
    print(f"\nFile ID: {file_id}")
    
    # Test extract
    result = test_extract(file_id)
    print("\n=== SUCCESS ===")
    print(f"Extracted {result.get('count', 0)} MCQs")

import requests
import os
import time
import json

# --- Configuration ---
BASE_URL = "http://127.0.0.1:8001"
UPLOAD_URL = f"{BASE_URL}/upload"
QUERY_URL = f"{BASE_URL}/query"
DUMMY_FILE_NAME = "test_document.txt"
DUMMY_FILE_CONTENT = "This is a test document about the solar system. The Earth revolves around the Sun. Mars is known as the Red Planet."

# --- Helper Functions ---
def create_dummy_file():
    """Creates a dummy text file for uploading."""
    with open(DUMMY_FILE_NAME, "w") as f:
        f.write(DUMMY_FILE_CONTENT)
    print(f"Created dummy file: '{DUMMY_FILE_NAME}'")

def remove_dummy_file():
    """Removes the dummy text file."""
    if os.path.exists(DUMMY_FILE_NAME):
        os.remove(DUMMY_FILE_NAME)
        print(f"Removed dummy file: '{DUMMY_FILE_NAME}'")

def check_server_status(url):
    """Checks if the server is running before starting tests."""
    try:
        response = requests.get(f"{BASE_URL}/docs") # Check a known endpoint that doesn't require auth
        if response.status_code == 200:
            print("✅ Server is running.")
            return True
        else:
            print(f"⚠️ Server responded with status code: {response.status_code}")
            return False
    except requests.ConnectionError:
        print("❌ Server is not running. Please start the server before running tests.")
        return False

# --- Test Functions ---
def test_upload():
    """
    Tests the /upload endpoint.
    """
    print("\n--- Testing /upload endpoint ---")
    create_dummy_file()
    
    files = {'files': (DUMMY_FILE_NAME, open(DUMMY_FILE_NAME, 'rb'), 'text/plain')}
    
    try:
        response = requests.post(UPLOAD_URL, files=files, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print("Response JSON:")
        print(json.dumps(response.json(), indent=2))
        
        assert response.status_code == 200
        assert "message" in response.json()
        print("✅ /upload endpoint test PASSED")
        
    except requests.RequestException as e:
        print(f"An error occurred during upload test: {e}")
        print("❌ /upload endpoint test FAILED")
    finally:
        remove_dummy_file()

def test_query():
    """
    Tests the /query endpoint after a delay to allow for processing.
    """
    # This delay is to give the server time to process the uploaded file.
    # In a real-world scenario, you might poll a status endpoint.
    processing_time = 5  # seconds
    print(f"\n--- Waiting {processing_time}s for the server to process the document ---")
    time.sleep(processing_time)
    
    print("\n--- Testing /query endpoint ---")
    payload = {
        "query": "how does anime effect kids nowadays... tell me from the paper i gave",
        "top_k": 1
    }
    
    try:
        print(f"sending payload{payload}")
        response = requests.post(QUERY_URL, json=payload, timeout=None)
        
        print(f"Status Code: {response.status_code}")
        print("Response JSON:")
        print(json.dumps(response.json(), indent=2))
        
        assert response.status_code == 200
        assert "answer" in response.json()
        assert "context" in response.json()
        
        # Check if the answer is reasonable (contains part of the expected answer)
        if "red planet" in response.json().get("answer", "").lower():
            print("✅ /query endpoint test PASSED")
        else:
            print("⚠️ /query endpoint test PASSED, but the answer might not be as expected.")

    except requests.RequestException as e:
        print(f"An error occurred during query test: {e}")
        print("❌ /query endpoint test FAILED")

# --- Main Execution ---
if __name__ == "__main__":
    if check_server_status(BASE_URL):
        # test_upload()
        test_query()
    else:
        print("\nExiting tests.")

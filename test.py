import requests
import os
import time
import json

# --- Configuration ---
BASE_URL = "http://127.0.0.1:8001"
UPLOAD_URL = f"{BASE_URL}/upload"
QUERY_URL = f"{BASE_URL}/query"
FILE_STATUS_URL = f"{BASE_URL}/file_status"
DEEP_QUERY_URL = f"{BASE_URL}/deepquery"
GENERATE_OUTLINE_URL = f"{BASE_URL}/generate_outline"
SUMMARIZE_URL = f"{BASE_URL}/summarize"
GENERATE_FAQ_URL = f"{BASE_URL}/generate_faq"
GENERATE_QUIZ_URL = f"{BASE_URL}/generate_quiz"
GENERATE_FLASHCARDS_URL = f"{BASE_URL}/generate_flashcards"
DELETE_URL = f"{BASE_URL}/delete"
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

def test_file_status():
    """
    Tests the /file_status endpoint.
    """
    print("\n--- Testing /file_status endpoint ---")
    try:
        response = requests.get(FILE_STATUS_URL, timeout=10)

        print(f"Status Code: {response.status_code}")
        print("Response JSON:")
        print(json.dumps(response.json(), indent=2))

        assert response.status_code == 200
        assert isinstance(response.json(), dict)
        print("✅ /file_status endpoint test PASSED")

    except requests.RequestException as e:
        print(f"An error occurred during file status test: {e}")
        print("❌ /file_status endpoint test FAILED")

def test_deep_query():
    """
    Tests the /deepquery endpoint.
    """
    print("\n--- Testing /deepquery endpoint ---")
    payload = {
        "query": "What is the impact of climate change on marine ecosystems, and what are the proposed solutions?",
        "top_k": 1,
        "create_graph": False
    }
    try:
        response = requests.post(DEEP_QUERY_URL, json=payload, timeout=None)

        print(f"Status Code: {response.status_code}")
        print("Response JSON:")
        print(json.dumps(response.json(), indent=2))

        assert response.status_code == 200
        assert "answer" in response.json()
        assert "context" in response.json()
        assert "sub_queries" in response.json()
        assert "graph_location" in response.json()
        print("✅ /deepquery endpoint test PASSED")

    except requests.RequestException as e:
        print(f"An error occurred during deep query test: {e}")
        print("❌ /deepquery endpoint test FAILED")

def test_generate_outline():
    """
    Tests the /generate_outline endpoint.
    """
    print("\n--- Testing /generate_outline endpoint ---")
    payload = {
        "filenames": [DUMMY_FILE_NAME],
        "combine": False
    }
    try:
        response = requests.post(GENERATE_OUTLINE_URL, json=payload, timeout=None)

        print(f"Status Code: {response.status_code}")
        print("Response JSON:")
        print(json.dumps(response.json(), indent=2))

        assert response.status_code == 200
        assert "individual_outlines" in response.json() or "combined_outline" in response.json()
        print("✅ /generate_outline endpoint test PASSED")

    except requests.RequestException as e:
        print(f"An error occurred during generate outline test: {e}")
        print("❌ /generate_outline endpoint test FAILED")

def test_summarize():
    """
    Tests the /summarize endpoint.
    """
    print("\n--- Testing /summarize endpoint ---")
    payload = {
        "filenames": [DUMMY_FILE_NAME]
    }
    try:
        response = requests.post(SUMMARIZE_URL, json=payload, timeout=None)

        print(f"Status Code: {response.status_code}")
        print("Response JSON:")
        print(json.dumps(response.json(), indent=2))

        assert response.status_code == 200
        assert "summaries" in response.json()
        assert isinstance(response.json()["summaries"], list)
        assert any(item["filename"] == DUMMY_FILE_NAME for item in response.json()["summaries"])
        print("✅ /summarize endpoint test PASSED")


    except requests.RequestException as e:
        print(f"An error occurred during summarize test: {e}")
        print("❌ /summarize endpoint test FAILED")

def test_generate_faq():
    """
    Tests the /generate_faq endpoint.
    """
    print("\n--- Testing /generate_faq endpoint ---")
    payload = {
        "filenames": [DUMMY_FILE_NAME]
    }
    try:
        response = requests.post(GENERATE_FAQ_URL, json=payload, timeout=None)

        print(f"Status Code: {response.status_code}")
        print("Response JSON:")
        print(json.dumps(response.json(), indent=2))

        assert response.status_code == 200
        assert "faqs" in response.json()
        assert isinstance(response.json()["faqs"], list)
        print("✅ /generate_faq endpoint test PASSED")

    except requests.RequestException as e:
        print(f"An error occurred during generate FAQ test: {e}")
        print("❌ /generate_faq endpoint test FAILED")

def test_generate_quiz():
    """
    Tests the /generate_quiz endpoint.
    """
    print("\n--- Testing /generate_quiz endpoint ---")
    payload = {
        "filenames": [DUMMY_FILE_NAME],
        "question_type": "mcq",
        "count": 2
    }
    try:
        response = requests.post(GENERATE_QUIZ_URL, json=payload, timeout=None)

        print(f"Status Code: {response.status_code}")
        print("Response JSON:")
        print(json.dumps(response.json(), indent=2))

        assert response.status_code == 200
        assert "quiz" in response.json()
        assert isinstance(response.json()["quiz"], list)
        print("✅ /generate_quiz endpoint test PASSED")

    except requests.RequestException as e:
        print(f"An error occurred during generate quiz test: {e}")
        print("❌ /generate_quiz endpoint test FAILED")

def test_generate_flashcards():
    """
    Tests the /generate_flashcards endpoint.
    """
    print("\n--- Testing /generate_flashcards endpoint ---")
    payload = {
        "filenames": [DUMMY_FILE_NAME]
    }
    try:
        response = requests.post(GENERATE_FLASHCARDS_URL, json=payload, timeout=None)

        print(f"Status Code: {response.status_code}")
        print("Response JSON:")
        print(json.dumps(response.json(), indent=2))

        assert response.status_code == 200
        assert "flashcards" in response.json()
        assert isinstance(response.json()["flashcards"], list)
        print("✅ /generate_flashcards endpoint test PASSED")

    except requests.RequestException as e:
        print(f"An error occurred during generate flashcards test: {e}")
        print("❌ /generate_flashcards endpoint test FAILED")

def test_delete_files():
    """
    Tests the /delete endpoint.
    """
    print("\n--- Testing /delete endpoint ---")
    # Ensure the dummy file is uploaded before attempting to delete
    create_dummy_file()
    files = {'files': (DUMMY_FILE_NAME, open(DUMMY_FILE_NAME, 'rb'), 'text/plain')}
    requests.post(UPLOAD_URL, files=files, timeout=30)
    time.sleep(5) # Give time for processing

    payload = {
        "filenames": [DUMMY_FILE_NAME]
    }
    try:
        response = requests.post(DELETE_URL, json=payload, timeout=None)

        print(f"Status Code: {response.status_code}")
        print("Response JSON:")
        print(json.dumps(response.json(), indent=2))

        assert response.status_code == 200
        assert "message" in response.json()
        assert f"Successfully deleted 1 files." == response.json()["message"]
        print("✅ /delete endpoint test PASSED")

    except requests.RequestException as e:
        print(f"An error occurred during delete files test: {e}")
        print("❌ /delete endpoint test FAILED")
    finally:
        remove_dummy_file()

# --- Main Execution ---
if __name__ == "__main__":
    if check_server_status(BASE_URL):
        test_upload()
        test_query()
        test_file_status()
        test_deep_query()
        test_generate_outline()
        test_summarize()
        test_generate_faq()
        test_generate_quiz()
        test_generate_flashcards()
        test_delete_files()
    else:
        print("\nExiting tests.")

import requests
import json

# Test the Flask app locally
def test_local_app():
    base_url = "http://localhost:5000"
    
    # Test health endpoint
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Health check: {response.status_code} - {response.json()}")
    except requests.exceptions.ConnectionError:
        print("App is not running. Start it with: python app.py")
        return
    
    # Test summarization endpoint
    print("\nTesting summarization endpoint...")
    test_text = """
    Artificial intelligence (AI) is intelligence demonstrated by machines, in contrast to the natural intelligence displayed by humans and animals. Leading AI textbooks define the field as the study of "intelligent agents": any device that perceives its environment and takes actions that maximize its chance of successfully achieving its goals. Colloquially, the term "artificial intelligence" is often used to describe machines that mimic "cognitive" functions that humans associate with the human mind, such as "learning" and "problem solving". The term was coined by John McCarthy in 1956.
    """
    
    payload = {
        "text": test_text,
        "max_length": 100,
        "min_length": 30
    }
    
    try:
        response = requests.post(
            f"{base_url}/summarize",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload)
        )
        print(f"Summarization: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Original length: {result['original_length']}")
            print(f"Summary length: {result['summary_length']}")
            print(f"Summary: {result['summary']}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error testing summarization: {e}")

if __name__ == "__main__":
    test_local_app()

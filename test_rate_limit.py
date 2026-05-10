import requests
import time

API_URL = "http://127.0.0.1:8000/chat"

def test_rate_limit():
    print(f"🚀 Starting rate limit test on {API_URL}...")
    print("Sending 7 requests (Limit is 5 per minute)...")
    
    for i in range(1, 8):
        try:
            # Increased timeout to 30s because the first RAG call can be slow
            response = requests.post(
                API_URL, 
                json={"message": f"Test message {i}", "history": []},
                timeout=30,
                stream=True
            )
            
            if response.status_code == 200:
                print(f"✅ Request {i}: Success (200 OK)")
                response.close() 
            elif response.status_code == 429:
                print(f"❌ Request {i}: Rate Limited! (429 Too Many Requests)")
            else:
                print(f"❓ Request {i}: Unexpected Status ({response.status_code})")
                
        except requests.exceptions.Timeout:
            print(f"⌛ Request {i}: Timeout - The server is taking too long to start the RAG stream.")
        except requests.exceptions.ConnectionError:
            print(f"🔌 Request {i}: Connection Error - Is the server running at {API_URL}?")
        except Exception as e:
            print(f"⚠️ Request {i}: Error - {str(e)}")
            break

if __name__ == "__main__":
    test_rate_limit()

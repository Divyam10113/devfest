import requests
import sys
import time
import json

def print_color(text, color="green"):
    colors = {"green": "\033[92m", "red": "\033[91m", "blue": "\033[94m", "end": "\033[0m"}
    print(f"{colors.get(color, '')}{text}{colors['end']}")

def check_service(name, url):
    print(f"Checking {name} at {url}...")
    try:
        response = requests.get(url + "/health", timeout=2)
        if response.status_code == 200:
            print_color(f"✔ {name} is ONLINE", "green")
            return True
        else:
            print_color(f"✘ {name} returned status {response.status_code}", "red")
            return False
    except requests.exceptions.ConnectionError:
        print_color(f"✘ {name} is OFFLINE (Connection Refused)", "red")
        return False
    except Exception as e:
        print_color(f"✘ {name} failed: {e}", "red")
        return False

def test_rag_flow():
    print("\n" + "="*50)
    print("Testing Compliance RAG Flow (Task 4 -> Task 3)")
    print("="*50)
    
    # Generic question that should work for ANY document
    query = "Summarize the key points of the provided documents."
    
    url = "http://localhost:8003/chat"
    payload = {
        "query": query, 
        "user_id": 123
    }
    
    print(f"Sending Query: '{payload['query']}' to {url}")
    
    try:
        start_time = time.time()
        response = requests.post(url, json=payload, timeout=60)
        duration = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            print_color(f"\n✔ Success! (Took {duration:.2f}s)", "green")
            print("\nResponse from LLM:")
            print_color(data["answer"], "blue")
            
            print(f"\nCitations Found: {len(data['citations'])}")
            for cit in data['citations']:
                print(f"- Page {cit['page']} of {cit['source']} (Score: {cit['score']:.2f})")
                
            if not data['citations']:
                print_color("\n⚠ No citations found.", "red")
                print("This means the system works, but your question wasn't relevant to the uploaded PDF.")
                print("Try asking a question specific to the content of your PDF.")
            else:
                print_color("\n✔ System is fully functional with RAG!", "green")
                
        else:
            print_color(f"\n✘ Request Failed: {response.text}", "red")
            
    except Exception as e:
        print_color(f"\n✘ Error: {e}", "red")

if __name__ == "__main__":
    print("Pre-flight Checks:")
    s3_status = check_service("Ingestion Service (Task 3)", "http://localhost:8002")
    s4_status = check_service("Compliance Service (Task 4)", "http://localhost:8003")
    
    if s3_status and s4_status:
        test_rag_flow()
    else:
        print("\n" + "-"*50)
        if not s3_status:
            print("⚠ Please run Task 3: `cd pdf_chunking && uvicorn app.main:app --port 8002 --loop asyncio`")
        if not s4_status:
            print("⚠ Please run Task 4: `cd compliance_service && uvicorn app.main:app --port 8003`")

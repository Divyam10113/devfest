"""
Simple test script to verify the Ingestion & Knowledge Service.
Run this after starting the service to check if everything works.
"""
import requests
import sys
import os

BASE_URL = "http://localhost:8002"


def test_health():
    """Test health check endpoint."""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        response.raise_for_status()
        data = response.json()
        print(f"✅ Health check passed: {data}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False


def test_upload(pdf_path):
    """Test PDF upload."""
    print(f"\n📤 Testing PDF upload: {pdf_path}")
    
    if not os.path.exists(pdf_path):
        print(f"❌ File not found: {pdf_path}")
        return False
    
    try:
        with open(pdf_path, 'rb') as f:
            files = {'file': (os.path.basename(pdf_path), f, 'application/pdf')}
            response = requests.post(f"{BASE_URL}/upload", files=files)
            response.raise_for_status()
            data = response.json()
            print(f"✅ Upload successful!")
            print(f"   - Document ID: {data['document_id']}")
            print(f"   - Parent chunks: {data['num_parent_chunks']}")
            print(f"   - Child chunks: {data['num_child_chunks']}")
            return True
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return False


def test_search(query):
    """Test search endpoint."""
    print(f"\n🔎 Testing search: '{query}'")
    try:
        payload = {
            "query": query,
            "top_k": 3,
            "include_parent": True
        }
        response = requests.post(f"{BASE_URL}/search", json=payload)
        response.raise_for_status()
        data = response.json()
        
        print(f"✅ Search successful! Found {data['num_results']} results:")
        for i, result in enumerate(data['results'][:3], 1):
            print(f"\n   Result {i}:")
            print(f"   - Score: {result['score']:.3f}")
            print(f"   - Page: {result['page']}")
            print(f"   - Source: {result['source']}")
            print(f"   - Text preview: {result['text'][:100]}...")
        
        return True
    except Exception as e:
        print(f"❌ Search failed: {e}")
        return False


def test_collections():
    """Test collection info endpoint."""
    print(f"\n📊 Testing collection info...")
    try:
        response = requests.get(f"{BASE_URL}/collections")
        response.raise_for_status()
        data = response.json()
        print(f"✅ Collection info retrieved:")
        print(f"   - Collection: {data['collection_name']}")
        print(f"   - Documents: {data['num_documents']}")
        print(f"   - Chunks: {data['num_chunks']}")
        return True
    except Exception as e:
        print(f"❌ Collection info failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("🧪 Ingestion & Knowledge Service Test Suite")
    print("=" * 60)
    
    # Test 1: Health check
    if not test_health():
        print("\n❌ Service is not running. Start it with:")
        print("   uvicorn app.main:app --reload --port 8002")
        sys.exit(1)
    
    # Test 2: Upload (optional - requires PDF)
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        test_upload(pdf_path)
    else:
        print("\n⚠️  Skipping upload test (no PDF provided)")
        print("   Run with: python test_service.py path/to/your.pdf")
    
    # Test 3: Collection info
    test_collections()
    
    # Test 4: Search (only if we have data)
    if len(sys.argv) > 2:
        query = sys.argv[2]
        test_search(query)
    else:
        print("\n⚠️  Skipping search test (no query provided)")
        print("   Run with: python test_service.py path/to/your.pdf 'your query'")
    
    print("\n" + "=" * 60)
    print("✅ Test suite completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()

import httpx
import asyncio
import os

# Configuration
GATEWAY_URL = "http://localhost:8000"
USER_EMAIL = "test_user_flow@example.com"
USER_NAME = "test_user_flow"
USER_PASSWORD = "password123"

async def main():
    print(f"🚀 Starting End-to-End Gateway Test...")
    print(f"Target: {GATEWAY_URL}")

    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. Register User
        print("\n[1] Registering User...")
        try:
            resp = await client.post(f"{GATEWAY_URL}/users/", json={
                "email": USER_EMAIL,
                "username": USER_NAME,
                "password": USER_PASSWORD
            })
            if resp.status_code == 201:
                print("✅ User Created")
                user_id = resp.json()["id"]
            elif resp.status_code == 400 and "already registered" in resp.text:
                print("ℹ️ User already exists, proceeding...")
                # Try login to get ID? Or just rely on login step.
                user_id = None # We'll find it or ignore needed
            else:
                print(f"❌ Registration Failed: {resp.text}")
                return
        except httpx.ConnectError:
             print("❌ Failed to connect to Gateway. Is it running on port 8000?")
             return

        # 2. Login
        print("\n[2] Logging In...")
        resp = await client.post(f"{GATEWAY_URL}/login", json={
            "identifier": USER_EMAIL,
            "password": USER_PASSWORD
        })
        if resp.status_code != 200:
            print(f"❌ Login Failed: {resp.text}")
            return
        
        token_data = resp.json()
        token = token_data["access_token"]
        print(f"✅ Logged In. Token: {token[:10]}...")
        
        # Decode token to get user_id if needed, or assume it's validated
        headers = {"Authorization": f"Bearer {token}"}

        # 3. Upload Document
        print("\n[3] Uploading Document...")
        # Create dummy PDF
        with open("test.pdf", "wb") as f:
            f.write(b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 4 0 R >> >> /MediaBox [0 0 612 792] /Contents 5 0 R >>\nendobj\n4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n5 0 obj\n<< /Length 44 >>\nstream\nBT /F1 24 Tf 100 700 Td (Hello World Compliance) Tj ET\nendstream\nendobj\nxref\n0 6\n0000000000 65535 f \n0000000010 00000 n \n0000000060 00000 n \n0000000157 00000 n \n0000000302 00000 n \n0000000389 00000 n \ntrailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n483\n%%EOF")

        files = {'file': ('test.pdf', open('test.pdf', 'rb'), 'application/pdf')}
        resp = await client.post(f"{GATEWAY_URL}/documents/upload", headers=headers, files=files)
        
        if resp.status_code == 202 or resp.status_code == 200:
             print(f"✅ Upload Success: {resp.json()}")
        else:
             print(f"❌ Upload Failed: {resp.text}")
             # Proceeding anyway as chat might work without specific doc context if fallback exists

        # 4. Multi-turn Chat Loop
        print("\n[4] Sending Multi-turn Chat Queries...")
        
        # Ensure we have a fresh user for this test to verify clean history
        import random
        rand_suffix = random.randint(10000, 99999)
        rand_user = f"chat_user_{rand_suffix}"
        print(f"   Creating User: {rand_user}")
        
        # Register
        resp = await client.post(f"{GATEWAY_URL}/users/", json={
            "email": f"{rand_user}@example.com",
            "username": rand_user,
            "password": "password123"
        })
        user_id = resp.json().get("id", 1) # Fallback if error (though we expect success)
        
        # Login
        resp = await client.post(f"{GATEWAY_URL}/login", json={
            "identifier": f"{rand_user}@example.com",
            "password": "password123"
        })
        token = resp.json()["access_token"]
        headers["Authorization"] = f"Bearer {token}"

        # 4. Interactive Chat Loop
        print("\n[4] Starting Interactive Chat Session (Type 'exit' to quit)...")
        
        # Ensure we have a fresh user for this test
        import random
        rand_suffix = random.randint(10000, 99999)
        rand_user = f"chat_user_{rand_suffix}"
        # print(f"   Creating User: {rand_user}") 
        
        # Register
        resp = await client.post(f"{GATEWAY_URL}/users/", json={
            "email": f"{rand_user}@example.com",
            "username": rand_user,
            "password": "password123"
        })
        user_id = resp.json().get("id", 1)
        
        # Login
        resp = await client.post(f"{GATEWAY_URL}/login", json={
            "identifier": f"{rand_user}@example.com",
            "password": "password123"
        })
        token = resp.json()["access_token"]
        
        while True:
            try:
                q = input("\nUser: ")
                if q.lower() in ['exit', 'quit']:
                    break
                
                print("   (Thinking...)")
                resp = await client.post(f"{GATEWAY_URL}/chat/", json={
                    "query": q,
                    "user_id": user_id,
                    "token": token
                })
                
                if resp.status_code == 200:
                    data = resp.json()
                    answer = data.get('answer', 'No answer')
                    citations = data.get('citations', [])
                    print(f"AI: {answer}")
                    if citations:
                         print(f"   [Citations: {len(citations)}]")
                else:
                    print(f"   ❌ Error: {resp.text}")
                    
            except EOFError:
                break

        # 5. History Verification
        print("\n[5] Checking History Persistence...")
        resp = await client.get(f"{GATEWAY_URL}/chat/history/{user_id}", headers=headers)
        if resp.status_code == 200:
            hist = resp.json()
            print(f"✅ History retrieved. Count: {len(hist)}")
            if len(hist) > 0:
                 print("   ✅ SUCCESS: History persists.")
            else:
                 print("   ⚠️ WARNING: No history found (Did you chat?).")
            
            # Print last interaction
            if hist:
                last = hist[-1]
                print(f"   Last Interaction: Q='{last['query']}' -> A='{last['answer'][:50]}...'")
        else:
            print(f"❌ History Failed: {resp.text}")

    print("\n🏁 Test Complete.")

if __name__ == "__main__":
    asyncio.run(main())

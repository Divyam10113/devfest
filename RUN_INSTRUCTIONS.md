# 🚀 Compliance Service Integration Instructions

This guide details how to run the fully integrated **Compliance Intelligence System** (Service 4 + Service 3), now powered by **Google Gemini**.

## 📋 Prerequisites

Ensure your `.env` files are configured:

1.  **`pdf_chunking/.env`** (Service 3)
    *   `LLAMA_CLOUD_API_KEY=...`
    *   `GOOGLE_API_KEY=...`

2.  **`compliance_service/.env`** (Service 4)
    *   `GOOGLE_API_KEY=...` (Same key as above)
    *   `INGESTION_SERVICE_URL=http://localhost:8002`

---

## 🏃‍♂️ Startup Guide

You must run these services in **separate terminals** to avoid port conflicts.

### 1. Start the Ingestion Service (Librarian)
**Terminal 1:**
```bash
cd devfest/pdf_chunking
uvicorn app.main:app --reload --port 8002 --loop asyncio
```
*Wait for: `Application startup complete`*

### 2. Start the Compliance Service (Brain)
**Terminal 2:**
```bash
cd devfest/compliance_service
uvicorn app.main:app --reload --port 8003
```
*Wait for: `Application startup complete`*

### 3. Verification
**Terminal 3:**
```bash
cd devfest
python3 verify_setup.py
```
*Expected Output:*
*   ✔ Ingestion Service is ONLINE
*   ✔ Compliance Service is ONLINE
*   ✔ Success! (With a detailed summary from Gemini 2.5)

---

## 🛠 Troubleshooting

*   **`Address already in use`**: You likely have a service running in another terminal. Find it and stop it (Ctrl+C), or run `pkill uvicorn` to stop everything.
*   **`404 models/gemini-1.5-flash not found`**: You are running an old version of the code. Restart Terminal 2.
*   **`np.float_ was removed`**: You need to downgrade numpy in Service 3: `pip install "numpy<2.0.0"`.
*   **Scores are 0.00 / 0.04**: This is **GOOD**. ChromaDB uses "Distance" scores, where 0 is perfect.

---

## 🏗 Architecture Status

| Service | Port | Status | AI Model |
| :--- | :--- | :--- | :--- |
| **Ingestion (Service 3)** | `8002` | ✅ Active | LlamaParse + Gemini Embeddings |
| **Compliance (Service 4)** | `8003` | ✅ Active | **Gemini 2.5 Flash Lite** |

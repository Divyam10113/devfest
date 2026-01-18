# Compliance Intelligence Service (Task 4)

This is the "Brain" of the architecture. It handles reasoning, context retrieval, and answer generation.

## Setup

1.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Environment Variables**
    Create a `.env` file in this directory:
    ```bash
    OPENAI_API_KEY=sk-your-key-here
    INGESTION_SERVICE_URL=http://localhost:8002
    ```

3.  **Run the Service**
    ```bash
    python -m app.main
    # OR
    uvicorn app.main:app --reload --port 8003
    ```

## API Specification

**Endpoint:** `POST /chat`
**Port:** `8003`

**Request:**
```json
{
  "query": "Can I work from remote locations?",
  "user_id": 1
}
```

**Response:**
```json
{
  "answer": "Yes, remote work is allowed up to 2 days a week...",
  "citations": [
    {
      "page": 4,
      "text": "Remote work policy...",
      "source": "hr_handbook.pdf",
      "score": 0.89
    }
  ],
  "conflict_detected": false
}
```

## Connection to Task 3
This service expects `pdf_chunking` service (Task 3) to be running on `http://localhost:8002`.

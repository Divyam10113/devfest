#!/bin/bash

# Setup script for Ingestion & Knowledge Service

echo "🚀 Setting up Ingestion & Knowledge Service..."

# Create data directory for PDFs
echo "📁 Creating data directory..."
mkdir -p data/pdfs
echo "✅ Created data/pdfs directory"

# Create ChromaDB directory
mkdir -p chroma_db
echo "✅ Created chroma_db directory"

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your LlamaParse API key:"
    echo "   - LLAMA_CLOUD_API_KEY (get from https://cloud.llamaindex.ai)"
    echo "   - No OpenAI key needed - we use FREE local embeddings! 🎉"
else
    echo "✅ .env file already exists"
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "📚 Next steps:"
echo "1. Add your LlamaParse API key to .env file"
echo "2. Place your default PDFs in data/pdfs/ directory"
echo "3. Run: uvicorn app.main:app --reload --port 8002"
echo ""
echo "💰 FREE local embeddings - zero API costs for embeddings!"
echo "The service will automatically load PDFs from data/pdfs/ at startup!"

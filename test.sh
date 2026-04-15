#!/bin/bash

# Noble API Test Script
# Simple bash script to test API endpoints with curl

SERVER_URL="${1:-http://localhost:8000}"
API_KEY="${2:-${API_KEY:-}}"

if [[ -n "$API_KEY" ]]; then
  AUTH_HEADER=(-H "X-API-Key: $API_KEY")
else
  AUTH_HEADER=()
fi

echo "Noble API Test Script"
echo "======================"
echo "Server: $SERVER_URL"
if [[ -n "$API_KEY" ]]; then
  echo "Auth: X-API-Key provided"
else
  echo "Auth: none (protected endpoints may fail)"
fi
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 1. Health Check
echo -e "${BLUE}1. Health Check${NC}"
curl -s "$SERVER_URL/health" | jq .
echo ""

# 2. Get Configuration
echo -e "${BLUE}2. Configuration${NC}"
curl -s "${AUTH_HEADER[@]}" "$SERVER_URL/config" | jq .
echo ""

# 3. List Models
echo -e "${BLUE}3. Available Models${NC}"
curl -s "${AUTH_HEADER[@]}" "$SERVER_URL/models" | jq '.hostname, .available_models.models | length'
echo ""

# 4. Generate via Ollama proxy
echo -e "${BLUE}4. Generate Request (Proxy -> Ollama)${NC}"
curl -s -X POST "$SERVER_URL/ollama/api/generate" \
  "${AUTH_HEADER[@]}" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemma4:26b",
    "prompt": "What is FastAPI? Answer in one sentence.",
    "temperature": 0.7,
    "num_predict": 100,
    "stream": false
  }' | jq .
echo ""

# 5. Embeddings via Ollama proxy
echo -e "${BLUE}5. Embedding Request (Proxy -> Ollama)${NC}"
curl -s -X POST "$SERVER_URL/ollama/api/embeddings" \
  "${AUTH_HEADER[@]}" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3-embedding:8b",
    "prompt": "FastAPI is a modern web framework"
  }' | jq '{dimension: .dimension, embedding_sample: .embedding[0:5]}'
echo ""

echo -e "${GREEN}✓ Test completed!${NC}"
echo ""
echo "To test with different server:"
echo "  API_KEY=your-key bash test.sh http://192.168.1.100:8000"
echo "  bash test.sh http://192.168.1.100:8000 your-key"

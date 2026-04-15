#!/bin/bash

# Noble API Test Script
# Simple bash script to test API endpoints with curl

SERVER_URL="${1:-http://localhost:8000}"

echo "Noble API Test Script"
echo "======================"
echo "Server: $SERVER_URL"
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
curl -s "$SERVER_URL/config" | jq .
echo ""

# 3. List Models
echo -e "${BLUE}3. Available Models${NC}"
curl -s "$SERVER_URL/models" | jq '.hostname, .current_llm, .current_embedding'
echo ""

# 4. Chat
echo -e "${BLUE}4. Chat Request${NC}"
curl -s -X POST "$SERVER_URL/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is FastAPI? Answer in one sentence.",
    "temperature": 0.7,
    "num_predict": 100
  }' | jq .
echo ""

# 5. Embeddings
echo -e "${BLUE}5. Embedding Request${NC}"
curl -s -X POST "$SERVER_URL/embed" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "FastAPI is a modern web framework"
  }' | jq '{model: .model, hostname: .hostname, dimension: .dimension, embedding_sample: .embedding[0:5]}'
echo ""

echo -e "${GREEN}✓ Test completed!${NC}"
echo ""
echo "To test with different server:"
echo "  bash test.sh http://192.168.1.100:8000"

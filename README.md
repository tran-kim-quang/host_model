# Noble API - FastAPI Server

FastAPI server for accessing LLM and Embedding models via network with hostname-based model selection.

## Features

✅ **Network Accessible** - Access from any machine on the LAN
✅ **Hostname-Based Model Selection** - Different models per host
✅ **LLM Chat** - Chat with LLM models
✅ **Embeddings** - Generate text embeddings
✅ **Auto Documentation** - Interactive API docs at `/docs`
✅ **Health Check** - Monitor server and Ollama status
✅ **CORS Enabled** - Work with cross-origin requests

## Installation

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Ensure Ollama is running**:
   ```bash
   # Make sure Ollama server is accessible
   # Default: http://localhost:11434
   # For LAN access, Ollama must be bound to 0.0.0.0
   ```

## Configuration

Edit `.env` to configure the API:

### Basic Settings

```env
# API Server
API_HOST=0.0.0.0
API_PORT=8000

# Ollama Connection
BASE_URL=http://localhost:11434

# Default Models
MODEL_LLM=gemma4:26b
MODEL_EMBEDDING=qwen3-embedding:8b
EMBEDDING_DIM=4096

DEBUG=false
```

### Hostname-Based Model Selection

Add configurations for different hosts:

```env
# Host 1 Configuration
HOST1_NAME=desktop
HOST1_MODEL_LLM=gemma4:26b

# Host 2 Configuration
HOST2_NAME=server
HOST2_MODEL_LLM=neural-chat:7b
```

When running on `desktop`, it will use `gemma4:26b`. On `server`, it will use `neural-chat:7b`.

Get your hostname:
```bash
# Linux/Mac
hostname

# Windows
hostname
```

## Running the Server

```bash
python main.py
```

The server will start on `http://0.0.0.0:8000`

With auto-reload (development):
```bash
DEBUG=true python main.py
```

## API Endpoints

### 1. Health Check
```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "hostname": "desktop",
  "llm_model": "gemma4:26b",
  "embedding_model": "qwen3-embedding:8b",
  "api_version": "1.0.0"
}
```

### 2. Get Configuration
```bash
curl http://localhost:8000/config
```

Shows current configuration loaded for this hostname.

### 3. List Available Models
```bash
curl http://localhost:8000/models
```

Lists all models available in Ollama.

### 4. Chat with LLM
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, how are you?",
    "temperature": 0.7,
    "top_p": 0.9
  }'
```

Request body:
- `message` (required): The prompt/message
- `model` (optional): Override the default model
- `temperature`: Controls randomness (0.0-1.0)
- `top_p`: Nucleus sampling parameter
- `top_k`: Top-k sampling
- `num_predict`: Max tokens to generate

Response:
```json
{
  "response": "Hello! I'm doing well, thank you for asking...",
  "model": "gemma4:26b",
  "hostname": "desktop"
}
```

### 5. Generate Embeddings
```bash
curl -X POST http://localhost:8000/embed \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This is a sample text for embedding"
  }'
```

Request body:
- `text` (required): The text to embed
- `model` (optional): Override the default model

Response:
```json
{
  "embedding": [0.123, 0.456, ...],
  "model": "qwen3-embedding:8b",
  "hostname": "desktop",
  "dimension": 4096
}
```

### 6. Interactive API Documentation
Open browser: `http://localhost:8000/docs`

## Accessing from Other Machines

### From same LAN:

1. **Find your server's IP**:
   ```bash
   # Linux/Mac
   ifconfig | grep "inet "
   
   # Windows
   ipconfig
   ```

2. **Make requests from other machine**:
   ```bash
   # Replace 192.168.1.100 with your server IP
   curl http://192.168.1.100:8000/health
   
   curl -X POST http://192.168.1.100:8000/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello"}'
   ```

### From different network:

Ensure your firewall allows port 8000:
```bash
# Linux - Allow port 8000
sudo ufw allow 8000

# Or forward ports through router if accessing from outside your network
```

## Example Usage (Python)

```python
import requests

API_URL = "http://192.168.1.100:8000"

# Health check
response = requests.get(f"{API_URL}/health")
print(response.json())

# Chat
chat_data = {
    "message": "What is machine learning?",
    "temperature": 0.7
}
response = requests.post(f"{API_URL}/chat", json=chat_data)
print(response.json())

# Embeddings
embed_data = {
    "text": "Machine learning is a subset of artificial intelligence"
}
response = requests.post(f"{API_URL}/embed", json=embed_data)
print(response.json())
```

## Troubleshooting

### Cannot connect to Ollama
- Make sure Ollama is running: `ollama serve`
- Check BASE_URL in .env (default: http://localhost:11434)
- For LAN access, Ollama must bind to 0.0.0.0

### Model not found
- Run `ollama pull model-name` to download
- Check available models: `curl http://localhost:8000/models`

### Cannot access from other machine
- Check firewall: `sudo ufw allow 8000`
- Use server's IP address, not localhost
- Ensure API_HOST=0.0.0.0 in .env

### CORS errors
- CORS is enabled for all origins by default
- Modify app.py to restrict if needed

## Project Structure

```
Noble/
├── .env                 # Configuration file
├── requirements.txt     # Python dependencies
├── config.py           # Configuration management
├── main.py             # FastAPI application
└── README.md           # This file
```

## Notes

- Hostname-based model selection happens at startup
- Different machines can use different models automatically
- All responses include hostname for debugging
- Health check verifies both API and Ollama connectivity


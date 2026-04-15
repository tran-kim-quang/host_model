# Quick Start Guide

## Option 1: Direct Python (Recommended for development)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Ensure Ollama is Running
```bash
ollama serve
# In another terminal:
ollama pull gemma4:26b
ollama pull qwen3-embedding:8b
```

### 3. Start the API Server
```bash
python main.py
```

Server starts on `http://0.0.0.0:8000`

### 4. Test the API

```bash
API_KEY="replace-with-strong-key"

# Health check
curl http://localhost:8000/health

# View API documentation
# Open browser to: http://localhost:8000/docs

# Test chat
curl -X POST http://localhost:8000/chat \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!"}'

# Test embeddings
curl -X POST http://localhost:8000/embed \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world"}'
```

### 5. Access from Another Machine
```bash
# Replace with your server IP
API_KEY="replace-with-strong-key"
curl http://192.168.1.100:8000/health

curl -X POST http://192.168.1.100:8000/chat \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello from LAN"}'
```

---

## Option 2: Docker (Recommended for production)

### 1. Build & Run with Docker Compose
```bash
docker-compose up -d
```

### 2. Check Status
```bash
docker-compose logs -f noble-api
```

### 3. Test
```bash
curl http://localhost:8000/health
```

### 4. Stop
```bash
docker-compose down
```

---

## Option 3: Python Client

### Run with Default Server
```bash
API_KEY=replace-with-strong-key python client.py
```

### Run with Custom Server
```bash
python client.py http://192.168.1.100:8000 replace-with-strong-key
```

---

## Option 4: Bash Script Test
```bash
API_KEY=replace-with-strong-key bash test.sh
bash test.sh http://192.168.1.100:8000 replace-with-strong-key
```

---

## Configuration for Multiple Hosts

Edit `.env` to configure different models for different hosts:

```env
# Host 1 (my laptop)
HOST1_NAME=my-laptop
HOST1_MODEL_LLM=gemma4:26b

# Host 2 (my server)
HOST2_NAME=my-server
HOST2_MODEL_LLM=neural-chat:7b

# Host 3 (another machine)
HOST3_NAME=worker-node
HOST3_MODEL_LLM=mistral:7b
```

Each machine automatically uses the configured model for its hostname!

---

## Access Control (API Key + Firewall)

### API Security (recommended)

Set in `.env`:

```env
SECURITY_ENABLED=true
API_KEYS=replace-with-strong-key
ALLOWED_CLIENT_HOSTNAMES=desktop,server
ALLOWED_CLIENT_IPS=192.168.1.10,192.168.1.11
```

Protected endpoints require `X-API-Key`: `/chat`, `/embed`, `/models`, `/config`.

### Allow port 8000 on Linux
```bash
sudo ufw allow 8000
```

### Or restrict to specific subnet
```bash
sudo ufw allow from 192.168.1.0/24 to any port 8000
```

---

## Troubleshooting

### Can't connect to Ollama?
- Make sure Ollama is running: `ollama serve`
- Check the BASE_URL in `.env`

### Models not found?
- Pull them: `ollama pull gemma4:26b`
- Check available: `curl http://localhost:11434/api/tags`

### Can't access from other machine?
- Use IP address, not hostname
- Check firewall: `sudo ufw status`
- Ensure API_HOST=0.0.0.0 in .env

### 401 or 403?
- 401: Missing/invalid API key, add `X-API-Key`
- 403: Client host/IP not in allowlist

### Interactive API docs not working?
- Open: `http://localhost:8000/docs` or `/redoc`

---

## Next Steps

1. ✅ Start the server
2. ✅ Test with curl or Python client
3. ✅ Configure hostname-based models if needed
4. ✅ Integrate into your applications

Enjoy! 🚀

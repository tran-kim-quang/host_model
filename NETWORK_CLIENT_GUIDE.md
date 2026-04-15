# Hướng dẫn Kết nối từ Máy Khác trên Mạng LAN

Tài liệu này giúp bạn kết nối từ máy tính khác trên cùng mạng LAN (Local Area Network) để sử dụng các model AI trên server.

---

## 📋 Yêu cầu

- ✅ Server đang chạy trên máy có Ollama
- ✅ Máy client và server cùng chung mạng LAN
- ✅ Firewall cho phép cổng 8000

---

## 1️⃣ Bước 1: Tìm IP Address của Server

### Trên Server (máy có Ollama)

**Linux/Mac:**
```bash
# Cách 1: Xem tất cả IP
ifconfig | grep "inet "

# Cách 2: Xem IP nhanh (nên là 192.168.x.x hoặc 10.x.x.x)
hostname -I
```

**Windows:**
```cmd
ipconfig
```

**Ví dụ kết quả:**
```
192.168.1.100    ← IP mạng LAN
10.0.0.50        ← IP khác (chọn cái đúng)
127.0.0.1        ← localhost (không dùng)
```

**👉 Lưu ý:** Chọn IP bắt đầu bằng `192.168.x.x` hoặc `10.x.x.x` (đó là IP mạng LAN)

---

## 2️⃣ Bước 2: Kiểm tra Server đang chạy

Trên máy server, chạy API:

```bash
python main.py
```

Bạn sẽ thấy:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

✅ Server đang chạy và lắng nghe trên tất cả network (0.0.0.0)

---

## 3️⃣ Bước 3: Kiểm tra kết nối từ máy khác

### Từ máy Client (máy khác)

**Test với curl:**
```bash
# Thay 192.168.1.100 bằng IP thực tế của server
curl http://192.168.1.100:8000/health
```

**Kết quả thành công:**
```json
{
  "status": "healthy",
  "hostname": "desktop",
  "llm_model": "gemma4:26b",
  "embedding_model": "qwen3-embedding:8b",
  "api_version": "1.0.0"
}
```

❌ **Nếu lỗi "Connection refused":**
- Kiểm tra IP có đúng không
- Kiểm tra server có đang chạy không
- Kiểm tra firewall

---

## 4️⃣ Cách 1: Gọi API bằng CURL

### Kiểm tra trạng thái

```bash
SERVER_IP="192.168.1.100"

# Health check
curl http://$SERVER_IP:8000/health
```

### Chat với LLM

```bash
curl -X POST http://192.168.1.100:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Xin chào! Bạn là ai?",
    "temperature": 0.7,
    "num_predict": 200
  }'
```

**Kết quả:**
```json
{
  "response": "Xin chào! Tôi là một trợ lý AI...",
  "model": "gemma4:26b",
  "hostname": "desktop"
}
```

### Tạo Embeddings

```bash
curl -X POST http://192.168.1.100:8000/embed \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Tôi yêu lập trình với Python"
  }'
```

**Kết quả:**
```json
{
  "embedding": [0.123, 0.456, ...],
  "model": "qwen3-embedding:8b",
  "hostname": "desktop",
  "dimension": 4096
}
```

### Xem cấu hình hiện tại

```bash
curl http://192.168.1.100:8000/config
```

### Liệt kê models có sẵn

```bash
curl http://192.168.1.100:8000/models
```

---

## 5️⃣ Cách 2: Gọi API bằng Python

### Tạo file `call_remote_api.py`

```python
import requests

# Cấu hình
SERVER_IP = "192.168.1.100"
SERVER_PORT = 8000
API_URL = f"http://{SERVER_IP}:{SERVER_PORT}"

# 1. Kiểm tra trạng thái
print("=== Health Check ===")
response = requests.get(f"{API_URL}/health")
print(response.json())
print()

# 2. Xem cấu hình
print("=== Configuration ===")
response = requests.get(f"{API_URL}/config")
print(response.json())
print()

# 3. Chat
print("=== Chat ===")
chat_data = {
    "message": "Giải thích webhook là gì?",
    "temperature": 0.7,
    "num_predict": 300
}
response = requests.post(f"{API_URL}/chat", json=chat_data)
result = response.json()
print(f"Model: {result['model']}")
print(f"Response: {result['response']}")
print()

# 4. Embeddings
print("=== Embeddings ===")
embed_data = {
    "text": "Machine learning là gì?"
}
response = requests.post(f"{API_URL}/embed", json=embed_data)
result = response.json()
print(f"Model: {result['model']}")
print(f"Dimension: {result['dimension']}")
print(f"Embedding sample: {result['embedding'][:5]}")
```

**Chạy:**
```bash
python call_remote_api.py
```

---

## 6️⃣ Cách 3: Web Browser - Interactive API Docs

**Mở browser:**
```
http://192.168.1.100:8000/docs
```

Bạn sẽ thấy:
- ✅ Danh sách tất cả endpoints
- ✅ Có thể test endpoint trực tiếp
- ✅ Xem request/response examples
- ✅ Tự động generate code

**Try it out:**
1. Click endpoint `/chat`
2. Click "Try it out"
3. Nhập message: "Hello"
4. Click "Execute"
5. Xem response

---

## 7️⃣ Hiểu về Hostname-Based Models

### Vấn đề

Nếu server chạy trên máy khác nhau, mỗi máy có thể chạy model khác:

```
Server trên "desktop"    → dùng gemma4:26b
Server trên "server"     → dùng neural-chat:7b
Server trên "gpu-node"   → dùng llama2:70b
```

### Giải pháp

Khi client gọi API:
```bash
curl http://192.168.1.100:8000/config
```

**Response sẽ chỉ rõ:**
```json
{
  "info": {
    "hostname": "desktop",
    "llm_model": "gemma4:26b",
    "embedding_model": "qwen3-embedding:8b"
  }
}
```

👉 **Client biết đang dùng model nào!**

### Cách dùng trong code

```python
import requests

API_URL = "http://192.168.1.100:8000"

# Lấy thông tin server
config = requests.get(f"{API_URL}/config").json()
server_hostname = config["info"]["hostname"]
current_model = config["info"]["llm_model"]

print(f"Server hostname: {server_hostname}")
print(f"Current model: {current_model}")

# Chat sẽ tự dùng model phù hợp
chat_response = requests.post(
    f"{API_URL}/chat",
    json={"message": "Hello"}
).json()

print(f"Used model: {chat_response['model']}")
```

---

## 8️⃣ Cấu hình Server cho Mạng LAN

### Trong `.env` trên Server

```env
# Cho phép tất cả máy trên mạng kết nối
API_HOST=0.0.0.0
API_PORT=8000

# Base URL - Ollama cũng phải lắng nghe trên 0.0.0.0
BASE_URL=http://localhost:11434
```

### Trong `main.py`

Nền tảng CORS (Cross-Origin Resource Sharing) đã được enable:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cho phép tất cả origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

✅ Server đã sẵn sàng cho mạng LAN!

---

## 9️⃣ Cấu hình Firewall (nếu cần)

### Linux - Mở cổng 8000

```bash
# Cho phép tất cả
sudo ufw allow 8000

# Hoặc chỉ cho phép subnet cụ thể
sudo ufw allow from 192.168.1.0/24 to any port 8000

# Kiểm tra
sudo ufw status
```

### Windows Firewall

1. Control Panel → Windows Defender Firewall → Allow an app
2. Add port 8000 (TCP)
3. Allow on Private networks

### macOS

```bash
# Thường không cần, nhưng nếu cần:
sudo nano /etc/pf.conf
# Thêm rule cho port 8000
```

---

## 🔟 Troubleshooting

### ❌ "Connection refused"

**Nguyên nhân:**
- Server chưa chạy
- IP sai
- Firewall chặn

**Giải pháp:**
```bash
# 1. Kiểm tra server đang chạy trên máy nào
ssh server-ip
ps aux | grep python

# 2. Kiểm tra ping
ping 192.168.1.100

# 3. Mở firewall
sudo ufw allow 8000

# 4. Restart server
python main.py
```

### ❌ "Connection timeout"

**Nguyên nhân:**
- Mạng LAN có vấn đề
- Máy server down
- IP không trên cùng subnet

**Giải pháp:**
```bash
# Kiểm tra subnet
ifconfig
# Nên là cùng dải 192.168.1.x hoặc cùng C-class

# Kiểm tra route
route -n
```

### ❌ "Model not found"

**Nguyên nhân:**
- Model chưa được pull

**Giải pháp:**
```bash
# Trên server
ollama pull gemma4:26b
ollama pull neural-chat:7b

# Verify
ollama list
```

### ❌ "Ollama not available"

**Nguyên nhân:**
- Ollama chưa chạy
- PORT sai

**Giải pháp:**
```bash
# Kiểm tra Ollama
ps aux | grep ollama

# Mở Ollama
ollama serve

# Kiểm tra PORT
curl http://localhost:11434/api/tags
```

---

## 1️⃣1️⃣ Ví dụ thực tế: Multi-Host Setup

### Server 1 (Desktop)
**IP:** 192.168.1.100
```env
API_HOST=0.0.0.0
API_PORT=8000
HOST1_NAME=desktop
HOST1_MODEL_LLM=gemma4:26b
```

### Server 2 (GPU Server)
**IP:** 192.168.1.101
```env
API_HOST=0.0.0.0
API_PORT=8000
HOST2_NAME=gpu-server
HOST2_MODEL_LLM=llama2:70b
```

### Client Code

```python
import requests

# Danh sách servers
servers = [
    "http://192.168.1.100:8000",
    "http://192.168.1.101:8000"
]

for server_url in servers:
    print(f"\n--- {server_url} ---")
    
    # Lấy info
    config = requests.get(f"{server_url}/config").json()
    hostname = config["info"]["hostname"]
    model = config["info"]["llm_model"]
    
    print(f"Hostname: {hostname}")
    print(f"Model: {model}")
    
    # Chat
    response = requests.post(
        f"{server_url}/chat",
        json={"message": "Hello", "num_predict": 50}
    ).json()
    
    print(f"Response: {response['response'][:100]}...")
```

---

## 1️⃣2️⃣ Performance Tips

### Tối ưu hóa tốc độ

```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Tạo session với retry logic
session = requests.Session()
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)

# Dùng session để gọi
response = session.post(
    "http://192.168.1.100:8000/chat",
    json={"message": "Hello"},
    timeout=60
)
```

### Batch Processing

```python
import requests
import concurrent.futures

server_url = "http://192.168.1.100:8000"
messages = [
    "Giải thích AI là gì?",
    "Giải thích ML là gì?",
    "Giải thích DL là gì?"
]

def chat(msg):
    return requests.post(
        f"{server_url}/chat",
        json={"message": msg}
    ).json()

# Gửi song song
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(chat, messages))

for msg, result in zip(messages, results):
    print(f"Q: {msg}")
    print(f"A: {result['response'][:100]}")
    print()
```

---

## 1️⃣3️⃣ Bảo mật (Optional)

Nếu muốn server chỉ cho phép kết nối từ IP cụ thể:

### Sửa firewall

```bash
# Chỉ cho phép 192.168.1.x
sudo ufw allow from 192.168.1.0/24 to any port 8000
```

### Hoặc sửa CORS trong `main.py`

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://192.168.1.100",
        "http://192.168.1.101",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 🎯 Checklist

Trước khi kết nối:

- [ ] Server đang chạy (`python main.py`)
- [ ] Ollama đang chạy (`ollama serve`)
- [ ] Tìm được IP server (`hostname -I` / `ifconfig`)
- [ ] Firewall mở cổng 8000 (`sudo ufw allow 8000`)
- [ ] Test ping thành công (`ping 192.168.1.x`)
- [ ] Health check thành công (`curl http://192.168.1.x:8000/health`)

✅ Mọi thứ OK, sẵn sàng sử dụng!

---

## 📚 Tham khảo thêm

- [README.md](README.md) - Tổng quan project
- [QUICKSTART.md](QUICKSTART.md) - Hướng dẫn nhanh
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Ollama Docs](https://ollama.ai/)

---

**Vấn đề hay câu hỏi? Kiểm tra phần Troubleshooting ở trên!** 🚀

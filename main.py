from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import logging
from pydantic import BaseModel
from typing import Optional, List
from config import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Noble API",
    description="API Server for LLM and Embedding Models",
    version="1.0.0"
)

# Enable CORS for cross-network access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for LAN access
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ Request/Response Models ============

class ChatRequest(BaseModel):
    message: str
    model: Optional[str] = None
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 40
    num_predict: int = 512
    stream: bool = False

class ChatResponse(BaseModel):
    response: str
    model: str
    hostname: str

class EmbedRequest(BaseModel):
    text: str
    model: Optional[str] = None

class EmbedResponse(BaseModel):
    embedding: List[float]
    model: str
    hostname: str
    dimension: int

class ModelInfo(BaseModel):
    name: str
    type: str

class HealthResponse(BaseModel):
    status: str
    hostname: str
    llm_model: str
    embedding_model: str
    api_version: str

# ============ Endpoints ============

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check API and Ollama server health"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{config.base_url}/api/tags", timeout=5.0)
            if response.status_code == 200:
                return HealthResponse(
                    status="healthy",
                    hostname=config.hostname,
                    llm_model=config.llm_model,
                    embedding_model=config.embedding_model,
                    api_version="1.0.0"
                )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Ollama server not available at {config.base_url}"
        )

@app.get("/models", response_model=dict)
async def get_models():
    """Get available models from Ollama"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{config.base_url}/api/tags", timeout=5.0)
            if response.status_code == 200:
                models = response.json()
                return {
                    "hostname": config.hostname,
                    "current_llm": config.llm_model,
                    "current_embedding": config.embedding_model,
                    "available_models": models
                }
    except Exception as e:
        logger.error(f"Failed to fetch models: {e}")
        raise HTTPException(status_code=503, detail="Cannot connect to Ollama")

@app.get("/config", response_model=dict)
async def get_config():
    """Get current configuration (hostname-based)"""
    return {
        "info": config.get_info(),
        "message": "Configuration loaded based on hostname"
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat with LLM model
    - Uses hostname-based model selection
    - If model not specified, uses configured default for this host
    """
    model = request.model or config.llm_model
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            payload = {
                "model": model,
                "prompt": request.message,
                "temperature": request.temperature,
                "top_p": request.top_p,
                "top_k": request.top_k,
                "num_predict": request.num_predict,
                "stream": False
            }
            
            response = await client.post(
                f"{config.base_url}/api/generate",
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                return ChatResponse(
                    response=result.get("response", ""),
                    model=model,
                    hostname=config.hostname
                )
            else:
                raise Exception(f"Model responded with {response.status_code}")
                
    except Exception as e:
        logger.error(f"Chat request failed: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Failed to get response from model '{model}': {str(e)}"
        )

@app.post("/embed", response_model=EmbedResponse)
async def embed(request: EmbedRequest):
    """
    Generate embeddings using embedding model
    - Uses hostname-based model selection
    - If model not specified, uses configured default for this host
    """
    model = request.model or config.embedding_model
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            payload = {
                "model": model,
                "prompt": request.text
            }
            
            response = await client.post(
                f"{config.base_url}/api/embeddings",
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                return EmbedResponse(
                    embedding=result.get("embedding", []),
                    model=model,
                    hostname=config.hostname,
                    dimension=len(result.get("embedding", []))
                )
            else:
                raise Exception(f"Model responded with {response.status_code}")
                
    except Exception as e:
        logger.error(f"Embed request failed: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Failed to get embeddings from model '{model}': {str(e)}"
        )

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "name": "Noble API",
        "version": "1.0.0",
        "hostname": config.hostname,
        "endpoints": {
            "health": "/health - Check server status",
            "config": "/config - View current configuration",
            "models": "/models - List available models",
            "chat": "/chat - Chat with LLM",
            "embed": "/embed - Generate embeddings",
            "docs": "/docs - Interactive API documentation"
        }
    }

# ============ Error Handlers ============

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return {
        "error": exc.detail,
        "status_code": exc.status_code,
        "hostname": config.hostname
    }

if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting API Server on {config.hostname}")
    logger.info(f"Configuration: {config.get_info()}")
    
    uvicorn.run(
        app,
        host=config.api_host,
        port=config.api_port,
        log_level="info",
        reload=config.debug
    )

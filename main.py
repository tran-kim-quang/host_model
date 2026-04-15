import socket
from fastapi import Depends, FastAPI, HTTPException, Request, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from fastapi.security import APIKeyHeader
import httpx
import logging
from pydantic import BaseModel
from config import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Noble API",
    description="API Server for LLM and Embedding Models",
    version="1.0.0"
)

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# Enable CORS for cross-network access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for LAN access
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ Response Models ============

class HealthResponse(BaseModel):
    status: str
    hostname: str
    base_url: str
    api_version: str


def _resolve_client_hostnames(client_ip: str) -> set[str]:
    """Resolve possible hostnames from client IP using reverse DNS."""
    if not client_ip:
        return set()

    try:
        primary, aliases, _ = socket.gethostbyaddr(client_ip)
        names = {primary.lower()}
        names.update(alias.lower() for alias in aliases)

        # Include short hostnames (before first dot) for easier matching in env.
        short_names = {name.split(".")[0] for name in names if "." in name}
        names.update(short_names)
        return names
    except Exception:
        return set()


async def authorize_request(
    request: Request,
    api_key: str = Security(api_key_header),
) -> None:
    """Authorize request by API key and optional hostname/IP allowlist."""
    if not config.security_enabled:
        return

    if not config.api_keys:
        raise HTTPException(
            status_code=500,
            detail="Security enabled but API_KEYS is empty",
        )

    if not api_key or api_key.lower() not in config.api_keys:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")

    client_ip = request.client.host if request.client else ""

    if config.allowed_client_ips and client_ip not in config.allowed_client_ips:
        raise HTTPException(status_code=403, detail="Client IP is not allowed")

    if config.allowed_client_hostnames:
        client_hosts = _resolve_client_hostnames(client_ip)
        if not client_hosts.intersection(config.allowed_client_hostnames):
            raise HTTPException(status_code=403, detail="Client hostname is not allowed")

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
                    base_url=config.base_url,
                    api_version="1.0.0"
                )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Ollama server not available at {config.base_url}"
        )

@app.get("/models", response_model=dict)
async def get_models(_: None = Depends(authorize_request)):
    """Get available models from Ollama"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{config.base_url}/api/tags", timeout=5.0)
            if response.status_code == 200:
                models = response.json()
                return {
                    "hostname": config.hostname,
                    "available_models": models
                }
    except Exception as e:
        logger.error(f"Failed to fetch models: {e}")
        raise HTTPException(status_code=503, detail="Cannot connect to Ollama")

@app.get("/config", response_model=dict)
async def get_config(_: None = Depends(authorize_request)):
    """Get current server/security configuration"""
    return {
        "info": config.get_info(),
        "message": "Server acts as authenticated gateway to Ollama"
    }

@app.api_route("/ollama/{ollama_path:path}", methods=["GET", "POST"])
async def proxy_to_ollama(
    ollama_path: str,
    request: Request,
    _: None = Depends(authorize_request),
):
    """
    Authenticated proxy endpoint.
    Client has full control over model selection and Ollama payload.
    """
    clean_path = ollama_path.lstrip("/")
    if not clean_path.startswith("api/"):
        raise HTTPException(status_code=400, detail="Only paths under /api are allowed")

    upstream_url = f"{config.base_url.rstrip('/')}/{clean_path}"
    query_params = dict(request.query_params)
    body = await request.body()

    upstream_headers = {}
    if request.headers.get("content-type"):
        upstream_headers["content-type"] = request.headers["content-type"]

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            upstream_response = await client.request(
                method=request.method,
                url=upstream_url,
                params=query_params,
                content=body,
                headers=upstream_headers,
            )
    except Exception as e:
        logger.error(f"Proxy request failed to {upstream_url}: {e}")
        raise HTTPException(status_code=503, detail="Cannot connect to Ollama")

    response_headers = {}
    content_type = upstream_response.headers.get("content-type")
    if content_type:
        response_headers["content-type"] = content_type

    return Response(
        content=upstream_response.content,
        status_code=upstream_response.status_code,
        headers=response_headers,
    )

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "name": "Noble API",
        "version": "1.0.0",
        "hostname": config.hostname,
        "mode": "authenticated-ollama-gateway",
        "endpoints": {
            "health": "/health - Check server status",
            "config": "/config - View current configuration (auth required)",
            "models": "/models - List available models (auth required)",
            "proxy": "/ollama/{path} - Proxy to Ollama API with full client control (auth required)",
            "example_generate": "POST /ollama/api/generate",
            "example_embeddings": "POST /ollama/api/embeddings",
            "docs": "/docs - Interactive API documentation"
        }
    }

# ============ Error Handlers ============

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "hostname": config.hostname
        }
    )

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

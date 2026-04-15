#!/usr/bin/env python3
"""
Noble API Client Example
Shows how to interact with the Noble API from another machine
"""

import requests
import json
import sys
import os
from typing import Optional

class NobleAPIClient:
    def __init__(self, server_url: str = "http://localhost:8000", api_key: Optional[str] = None):
        self.server_url = server_url.rstrip('/')
        self.session = requests.Session()
        self.api_key = api_key
        if self.api_key:
            self.session.headers.update({"X-API-Key": self.api_key})
    
    def health_check(self) -> dict:
        """Check server health"""
        try:
            response = self.session.get(f"{self.server_url}/health")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_config(self) -> dict:
        """Get current configuration"""
        try:
            response = self.session.get(f"{self.server_url}/config")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def list_models(self) -> dict:
        """List available models"""
        try:
            response = self.session.get(f"{self.server_url}/models")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def ollama_request(self, path: str, payload: Optional[dict] = None, method: str = "POST") -> dict:
        """Send direct request to Ollama through authenticated gateway."""
        try:
            clean_path = path.lstrip("/")
            response = self.session.request(
                method=method,
                url=f"{self.server_url}/ollama/{clean_path}",
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def generate(self, model: str, prompt: str, **kwargs) -> dict:
        """Generate text with full control over Ollama payload fields."""
        payload = {
            "model": model,
            "prompt": prompt,
            **kwargs,
        }
        return self.ollama_request("api/generate", payload=payload, method="POST")

    def embeddings(self, model: str, text: str, **kwargs) -> dict:
        """Create embeddings with full control over Ollama payload fields."""
        payload = {
            "model": model,
            "prompt": text,
            **kwargs,
        }
        return self.ollama_request("api/embeddings", payload=payload, method="POST")


def print_json(data: dict, indent: int = 2):
    """Pretty print JSON"""
    print(json.dumps(data, indent=indent, ensure_ascii=False))


def main():
    # Change to your server IP/hostname if accessing from another machine
    # Examples:
    # - Local: http://localhost:8000
    # - LAN: http://192.168.1.100:8000
    # - Remote: http://your-server.com:8000
    
    server_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    api_key = sys.argv[2] if len(sys.argv) > 2 else os.getenv("API_KEY")
    
    print(f"Connecting to Noble API at: {server_url}")
    if api_key:
        print("Authentication: X-API-Key enabled\n")
    else:
        print("Authentication: none (protected endpoints may fail)\n")
    
    client = NobleAPIClient(server_url, api_key=api_key)
    
    # 1. Health check
    print("=" * 50)
    print("1. Health Check")
    print("=" * 50)
    result = client.health_check()
    print_json(result)
    print()
    
    # 2. Get configuration
    print("=" * 50)
    print("2. Configuration")
    print("=" * 50)
    result = client.get_config()
    print_json(result)
    print()
    
    # 3. List models
    print("=" * 50)
    print("3. Available Models")
    print("=" * 50)
    result = client.list_models()
    if "error" not in result:
        print(f"Current hostname: {result.get('hostname')}")
        if "available_models" in result:
            print(f"Available models: {len(result['available_models'].get('models', []))} models")
    else:
        print_json(result)
    print()
    
    models = result.get("available_models", {}).get("models", []) if isinstance(result, dict) else []
    model_name = models[0]["name"] if models else "gemma4:26b"

    # 4. Generate
    print("=" * 50)
    print("4. Generate Test (Proxy -> Ollama)")
    print("=" * 50)
    print(f"Model: {model_name}")
    print("Query: 'What is API?'")
    result = client.generate(
        model=model_name,
        prompt="What is API? (answer in 2 sentences)",
        stream=False,
        num_predict=120,
    )
    print_json(result)
    print()
    
    # 5. Embeddings
    print("=" * 50)
    print("5. Embedding Test (Proxy -> Ollama)")
    print("=" * 50)
    print("Text: 'API is a software interface'")
    embedding_model = "qwen3-embedding:8b"
    result = client.embeddings(embedding_model, "API is a software interface")
    if "error" not in result:
        embedding = result.get("embedding", [])
        print(f"Model: {embedding_model}")
        print(f"Embedding dimension: {result.get('dimension')}")
        print(f"First 5 values: {embedding[:5]}")
    else:
        print_json(result)
    print()
    
    print("=" * 50)
    print("✓ Client demonstration completed!")
    print("=" * 50)


if __name__ == "__main__":
    main()

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
    
    def chat(
        self,
        message: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        top_p: float = 0.9,
        top_k: int = 40,
        num_predict: int = 512
    ) -> dict:
        """Chat with LLM"""
        try:
            payload = {
                "message": message,
                "temperature": temperature,
                "top_p": top_p,
                "top_k": top_k,
                "num_predict": num_predict
            }
            if model:
                payload["model"] = model
            
            response = self.session.post(
                f"{self.server_url}/chat",
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def embed(self, text: str, model: Optional[str] = None) -> dict:
        """Generate embeddings"""
        try:
            payload = {"text": text}
            if model:
                payload["model"] = model
            
            response = self.session.post(
                f"{self.server_url}/embed",
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}


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
    print("2. Configuration (Hostname-based)")
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
        print(f"Current LLM: {result.get('current_llm')}")
        print(f"Current Embedding: {result.get('current_embedding')}")
        if "available_models" in result:
            print(f"Available models: {len(result['available_models'].get('models', []))} models")
    else:
        print_json(result)
    print()
    
    # 4. Chat
    print("=" * 50)
    print("4. Chat Test")
    print("=" * 50)
    print("Query: 'What is API?'")
    result = client.chat("What is API? (answer in 2 sentences)")
    print_json(result)
    print()
    
    # 5. Embeddings
    print("=" * 50)
    print("5. Embedding Test")
    print("=" * 50)
    print("Text: 'API is a software interface'")
    result = client.embed("API is a software interface")
    if "error" not in result:
        embedding = result.get("embedding", [])
        print(f"Model: {result.get('model')}")
        print(f"Hostname: {result.get('hostname')}")
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

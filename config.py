import os
from socket import gethostname
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration management with hostname-based model selection"""
    
    def __init__(self):
        self.hostname = gethostname().lower()
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        
        # API Server config
        self.api_host = os.getenv("API_HOST", "0.0.0.0")
        self.api_port = int(os.getenv("API_PORT", "8000"))
        
        # Base URL for Ollama
        self.base_url = os.getenv("BASE_URL", "http://localhost:11434")

        # Access control
        self.security_enabled = os.getenv("SECURITY_ENABLED", "false").lower() == "true"
        self.api_keys = self._parse_csv_env("API_KEYS")
        self.allowed_client_hostnames = self._parse_csv_env("ALLOWED_CLIENT_HOSTNAMES")
        self.allowed_client_ips = self._parse_csv_env("ALLOWED_CLIENT_IPS")
        
        # Default models
        self.default_llm_model = os.getenv("MODEL_LLM", "gemma4:26b")
        self.default_embedding_model = os.getenv("MODEL_EMBEDDING", "qwen3-embedding:8b")
        self.embedding_dim = int(os.getenv("EMBEDDING_DIM", "4096"))
        
        # Get hostname-based configuration
        self.llm_model = self._get_model_for_host("MODEL_LLM")
        self.embedding_model = self._get_model_for_host("MODEL_EMBEDDING")

    def _parse_csv_env(self, env_name: str) -> set[str]:
        """Parse comma-separated values from env into normalized set."""
        raw = os.getenv(env_name, "")
        values = [item.strip().lower() for item in raw.split(",") if item.strip()]
        return set(values)
    
    def _get_model_for_host(self, model_type: str) -> str:
        """
        Get model name based on hostname.
        Checks for HOST{N}_NAME matching current hostname,
        then uses HOST{N}_MODEL_{TYPE}
        """
        # Check for hostname matches
        for i in range(1, 10):  # Support up to 9 hosts
            host_name = os.getenv(f"HOST{i}_NAME", "").lower()
            if host_name and host_name == self.hostname:
                model = os.getenv(f"HOST{i}_{model_type}")
                if model:
                    return model
        
        # Fall back to default
        if model_type == "MODEL_LLM":
            return self.default_llm_model
        elif model_type == "MODEL_EMBEDDING":
            return self.default_embedding_model
        
        return ""
    
    def get_info(self) -> dict:
        """Return configuration info"""
        return {
            "hostname": self.hostname,
            "api_host": self.api_host,
            "api_port": self.api_port,
            "base_url": self.base_url,
            "llm_model": self.llm_model,
            "embedding_model": self.embedding_model,
            "embedding_dim": self.embedding_dim,
            "security_enabled": self.security_enabled,
            "allowed_client_hostnames": sorted(self.allowed_client_hostnames),
            "allowed_client_ips": sorted(self.allowed_client_ips),
            "api_key_count": len(self.api_keys),
            "debug": self.debug
        }


# Initialize global config
config = Config()

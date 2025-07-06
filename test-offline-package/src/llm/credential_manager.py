"""
Credential Manager for X-Pull-Request-Reviewer
Handles API keys and authentication for different LLM providers.
"""

import os
import json
import getpass
import keyring
import logging
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class CredentialManager:
    """Manages credentials for different LLM providers"""
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize credential manager
        
        Args:
            config_dir: Directory to store credentials (default: ~/.xprr)
        """
        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            self.config_dir = Path.home() / ".xprr"
        
        self.config_dir.mkdir(exist_ok=True)
        self.credentials_file = self.config_dir / "credentials.json"
        self._load_credentials()
    
    def _load_credentials(self):
        """Load credentials from file"""
        if self.credentials_file.exists():
            try:
                with open(self.credentials_file, 'r') as f:
                    self.credentials = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Failed to load credentials file: {e}")
                self.credentials = {}
        else:
            self.credentials = {}
    
    def _save_credentials(self):
        """Save credentials to file"""
        try:
            with open(self.credentials_file, 'w') as f:
                json.dump(self.credentials, f, indent=2)
        except IOError as e:
            logger.error(f"Failed to save credentials: {e}")
    
    def get_credential(self, provider: str, credential_type: str = "api_key") -> Optional[str]:
        """
        Get a credential for a specific provider
        
        Args:
            provider: The LLM provider (e.g., 'google_code_assist', 'gemini_cli', 'ollama')
            credential_type: Type of credential (e.g., 'api_key', 'project_id')
            
        Returns:
            The credential value or None if not found
        """
        # First try environment variables
        env_var = f"{provider.upper()}_{credential_type.upper()}"
        if env_var in os.environ:
            return os.environ[env_var]
        
        # Then try keyring
        keyring_key = f"xprr_{provider}_{credential_type}"
        try:
            credential = keyring.get_password("x-pull-request-reviewer", keyring_key)
            if credential:
                return credential
        except Exception as e:
            logger.debug(f"Keyring access failed: {e}")
        
        # Finally try local file
        provider_creds = self.credentials.get(provider, {})
        return provider_creds.get(credential_type)
    
    def set_credential(self, provider: str, credential_type: str, value: str, 
                      use_keyring: bool = True, use_file: bool = True):
        """
        Set a credential for a specific provider
        
        Args:
            provider: The LLM provider
            credential_type: Type of credential
            value: The credential value
            use_keyring: Whether to store in system keyring
            use_file: Whether to store in local file
        """
        # Store in keyring if requested
        if use_keyring:
            try:
                keyring_key = f"xprr_{provider}_{credential_type}"
                keyring.set_password("x-pull-request-reviewer", keyring_key, value)
                logger.info(f"Stored {credential_type} for {provider} in keyring")
            except Exception as e:
                logger.warning(f"Failed to store credential in keyring: {e}")
        
        # Store in local file if requested
        if use_file:
            if provider not in self.credentials:
                self.credentials[provider] = {}
            self.credentials[provider][credential_type] = value
            self._save_credentials()
            logger.info(f"Stored {credential_type} for {provider} in local file")
    
    def prompt_for_credentials(self, provider: str) -> Dict[str, str]:
        """
        Prompt user for credentials for a specific provider
        
        Args:
            provider: The LLM provider
            
        Returns:
            Dictionary of credentials
        """
        credentials = {}
        
        if provider == "google_code_assist":
            print(f"\n🔑 Google Code Assist Credentials")
            print("=" * 50)
            
            api_key = getpass.getpass("Enter your Google Code Assist API key: ")
            if api_key:
                credentials["api_key"] = api_key
                self.set_credential(provider, "api_key", api_key)
            
            project_id = input("Enter your Google Cloud project ID (optional): ").strip()
            if project_id:
                credentials["project_id"] = project_id
                self.set_credential(provider, "project_id", project_id)
        
        elif provider == "gemini_cli":
            print(f"\n🔑 Gemini CLI Credentials")
            print("=" * 50)
            
            api_key = getpass.getpass("Enter your Gemini API key: ")
            if api_key:
                credentials["api_key"] = api_key
                self.set_credential(provider, "api_key", api_key)
        
        elif provider == "ollama":
            print(f"\n🔑 Ollama Configuration")
            print("=" * 50)
            
            host = input("Enter Ollama host (default: localhost): ").strip() or "localhost"
            credentials["host"] = host
            self.set_credential(provider, "host", host)
            
            port = input("Enter Ollama port (default: 11434): ").strip() or "11434"
            credentials["port"] = port
            self.set_credential(provider, "port", port)
            
            model = input("Enter Ollama model (default: codellama): ").strip() or "codellama"
            credentials["model"] = model
            self.set_credential(provider, "model", model)
        
        return credentials
    
    def check_credentials(self, provider: str) -> bool:
        """
        Check if credentials are available for a provider
        
        Args:
            provider: The LLM provider
            
        Returns:
            True if credentials are available, False otherwise
        """
        if provider == "google_code_assist":
            api_key = self.get_credential(provider, "api_key")
            return api_key is not None
        
        elif provider == "gemini_cli":
            api_key = self.get_credential(provider, "api_key")
            return api_key is not None
        
        elif provider == "ollama":
            # Ollama doesn't require API key, just check if it's running
            return True
        
        return False
    
    def list_providers(self) -> Dict[str, bool]:
        """
        List all providers and their credential status
        
        Returns:
            Dictionary mapping provider names to credential availability
        """
        providers = {
            "ollama": self.check_credentials("ollama"),
            "google_code_assist": self.check_credentials("google_code_assist"),
            "gemini_cli": self.check_credentials("gemini_cli")
        }
        return providers
    
    def remove_credential(self, provider: str, credential_type: str):
        """
        Remove a credential
        
        Args:
            provider: The LLM provider
            credential_type: Type of credential
        """
        # Remove from keyring
        try:
            keyring_key = f"xprr_{provider}_{credential_type}"
            keyring.delete_password("x-pull-request-reviewer", keyring_key)
        except Exception as e:
            logger.debug(f"Failed to remove from keyring: {e}")
        
        # Remove from local file
        if provider in self.credentials and credential_type in self.credentials[provider]:
            del self.credentials[provider][credential_type]
            if not self.credentials[provider]:
                del self.credentials[provider]
            self._save_credentials()
    
    def clear_all_credentials(self):
        """Clear all stored credentials"""
        # Clear keyring
        try:
            keyring.delete_password("x-pull-request-reviewer", "xprr_google_code_assist_api_key")
            keyring.delete_password("x-pull-request-reviewer", "xprr_gemini_cli_api_key")
        except Exception as e:
            logger.debug(f"Failed to clear keyring: {e}")
        
        # Clear local file
        self.credentials = {}
        self._save_credentials()
        
        logger.info("All credentials cleared")


# Global credential manager instance
_credential_manager = None

def get_credential_manager() -> CredentialManager:
    """Get the global credential manager instance"""
    global _credential_manager
    if _credential_manager is None:
        _credential_manager = CredentialManager()
    return _credential_manager 
"""
Unified LLM Client for X-Pull-Request-Reviewer
Provides a unified interface for different LLM providers.
"""

import os
import logging
from typing import List, Tuple, Optional, Dict, Any
from .ollama_client import query_ollama_for_review
from .google_code_assist_client import query_google_code_assist_for_review
from .gemini_cli_client import query_gemini_cli_for_review
from .credential_manager import get_credential_manager

logger = logging.getLogger(__name__)

class UnifiedLLMClient:
    """Unified client for different LLM providers"""
    
    def __init__(self, provider: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        """
        Initialize unified LLM client
        
        Args:
            provider: LLM provider to use (ollama, google_code_assist, gemini_cli)
            config: Configuration dictionary
        """
        self.config = config or {}
        self.credential_manager = get_credential_manager()
        
        # Determine provider
        if provider:
            self.provider = provider
        else:
            self.provider = self.config.get('llm', {}).get('provider', 'ollama')
        
        # Set environment variables for the selected provider
        self._setup_environment()
        
        logger.info(f"Initialized UnifiedLLMClient with provider: {self.provider}")
    
    def _setup_environment(self):
        """Set up environment variables for the selected provider"""
        if self.provider == "google_code_assist":
            api_key = self.credential_manager.get_credential("google_code_assist", "api_key")
            if api_key:
                os.environ['GOOGLE_CODE_ASSIST_API_KEY'] = api_key
            
            project_id = self.credential_manager.get_credential("google_code_assist", "project_id")
            if project_id:
                os.environ['GOOGLE_CLOUD_PROJECT'] = project_id
        
        elif self.provider == "gemini_cli":
            api_key = self.credential_manager.get_credential("gemini_cli", "api_key")
            if api_key:
                os.environ['GEMINI_API_KEY'] = api_key
        
        elif self.provider == "ollama":
            host = self.credential_manager.get_credential("ollama", "host") or "localhost"
            port = self.credential_manager.get_credential("ollama", "port") or "11434"
            model = self.credential_manager.get_credential("ollama", "model") or "codellama"
            
            os.environ['LLM_HOST'] = host
            os.environ['LLM_PORT'] = port
            os.environ['LLM_MODEL'] = model
            
            # Ensure Ollama server is running
            from .ollama_client import ensure_ollama_server
            if not ensure_ollama_server():
                logger.error("Failed to start Ollama server")
                print("[ERROR] Failed to start Ollama server")
    
    def query_for_review(self, prompt: str, diff: str, file_path: Optional[str] = None) -> Tuple[List[Tuple], str]:
        """
        Query the selected LLM provider for code review
        
        Args:
            prompt: The review prompt
            diff: The code diff to review
            file_path: Optional file path for context
            
        Returns:
            Tuple of (line_comments, summary)
        """
        logger.info(f"Querying {self.provider} for code review...")
        
        try:
            if self.provider == "ollama":
                return query_ollama_for_review(prompt, diff)
            
            elif self.provider == "google_code_assist":
                return query_google_code_assist_for_review(prompt, diff, file_path)
            
            elif self.provider == "gemini_cli":
                return query_gemini_cli_for_review(prompt, diff, file_path)
            
            else:
                logger.error(f"Unknown LLM provider: {self.provider}")
                return [], f"Error: Unknown LLM provider '{self.provider}'"
                
        except Exception as e:
            logger.error(f"Error querying {self.provider}: {e}")
            return [], f"Error: Failed to query {self.provider} - {e}"
    
    def test_connection(self) -> bool:
        """
        Test connection to the selected LLM provider
        
        Returns:
            True if connection is successful, False otherwise
        """
        logger.info(f"Testing connection to {self.provider}...")
        
        try:
            if self.provider == "ollama":
                # Ensure Ollama server is running first
                from .ollama_client import ensure_ollama_server
                if not ensure_ollama_server():
                    logger.error("Failed to start Ollama server for connection test")
                    return False
                
                # For Ollama, we'll do a simple test query
                test_prompt = "Please respond with 'OK' if you can see this message."
                test_diff = "This is a test diff for connection testing."
                
                line_comments, summary = query_ollama_for_review(test_prompt, test_diff)
                
                if "Error:" in summary:
                    logger.error(f"Ollama connection test failed: {summary}")
                    return False
                
                logger.info("Ollama connection test successful")
                return True
            
            elif self.provider == "google_code_assist":
                from .google_code_assist_client import GoogleCodeAssistClient
                client = GoogleCodeAssistClient()
                return client.test_connection()
            
            elif self.provider == "gemini_cli":
                from .gemini_cli_client import GeminiCLIClient
                client = GeminiCLIClient()
                return client.test_connection()
            
            else:
                logger.error(f"Unknown LLM provider: {self.provider}")
                return False
                
        except Exception as e:
            logger.error(f"Connection test failed for {self.provider}: {e}")
            return False
    
    def get_available_providers(self) -> Dict[str, bool]:
        """
        Get list of available providers and their status
        
        Returns:
            Dictionary mapping provider names to availability status
        """
        return self.credential_manager.list_providers()
    
    def switch_provider(self, new_provider: str) -> bool:
        """
        Switch to a different LLM provider
        
        Args:
            new_provider: The new provider to switch to
            
        Returns:
            True if switch was successful, False otherwise
        """
        if new_provider not in ["ollama", "google_code_assist", "gemini_cli"]:
            logger.error(f"Unknown provider: {new_provider}")
            return False
        
        # Check if credentials are available
        if not self.credential_manager.check_credentials(new_provider):
            logger.warning(f"Credentials not available for {new_provider}")
            return False
        
        # Switch provider
        old_provider = self.provider
        self.provider = new_provider
        self._setup_environment()
        
        logger.info(f"Switched from {old_provider} to {new_provider}")
        return True
    
    def setup_provider(self, provider: str) -> bool:
        """
        Set up a new LLM provider by prompting for credentials
        
        Args:
            provider: The provider to set up
            
        Returns:
            True if setup was successful, False otherwise
        """
        if provider not in ["ollama", "google_code_assist", "gemini_cli"]:
            logger.error(f"Unknown provider: {provider}")
            return False
        
        try:
            # Prompt for credentials
            credentials = self.credential_manager.prompt_for_credentials(provider)
            
            if credentials:
                logger.info(f"Successfully set up {provider}")
                return True
            else:
                logger.warning(f"No credentials provided for {provider}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to set up {provider}: {e}")
            return False


def get_llm_client(provider: Optional[str] = None, config: Optional[Dict[str, Any]] = None) -> UnifiedLLMClient:
    """
    Get a unified LLM client instance
    
    Args:
        provider: LLM provider to use
        config: Configuration dictionary
        
    Returns:
        UnifiedLLMClient instance
    """
    return UnifiedLLMClient(provider, config)


def query_llm_for_review(prompt: str, diff: str, file_path: Optional[str] = None, 
                        provider: Optional[str] = None, config: Optional[Dict[str, Any]] = None) -> Tuple[List[Tuple], str]:
    """
    Convenience function to query LLM for code review
    
    Args:
        prompt: The review prompt
        diff: The code diff to review
        file_path: Optional file path for context
        provider: LLM provider to use
        config: Configuration dictionary
        
    Returns:
        Tuple of (line_comments, summary)
    """
    client = get_llm_client(provider, config)
    return client.query_for_review(prompt, diff, file_path) 
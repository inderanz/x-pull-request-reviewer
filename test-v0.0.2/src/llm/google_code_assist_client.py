"""
Google Code Assist LLM Client for X-Pull-Request-Reviewer
Handles authentication and API calls to Google Code Assist for code review.
"""

import os
import json
import requests
import re
from typing import List, Tuple, Optional
import subprocess
import tempfile
import logging

logger = logging.getLogger(__name__)

class GoogleCodeAssistClient:
    """Client for Google Code Assist API"""
    
    def __init__(self, api_key: Optional[str] = None, project_id: Optional[str] = None):
        """
        Initialize Google Code Assist client
        
        Args:
            api_key: Google Cloud API key (if not provided, will try to get from environment)
            project_id: Google Cloud project ID (if not provided, will try to get from environment)
        """
        self.api_key = api_key or os.environ.get('GOOGLE_CODE_ASSIST_API_KEY')
        self.project_id = project_id or os.environ.get('GOOGLE_CLOUD_PROJECT')
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        self.model = "gemini-1.5-flash"
        
        if not self.api_key:
            raise ValueError("Google Code Assist API key is required. Set GOOGLE_CODE_ASSIST_API_KEY environment variable or pass api_key parameter.")
        
        if not self.project_id:
            logger.warning("Google Cloud project ID not set. Some features may not work properly.")
    
    def _get_auth_headers(self) -> dict:
        """Get authentication headers for API requests"""
        return {
            "Content-Type": "application/json"
        }
    
    def query_for_review(self, prompt: str, diff: str, file_path: Optional[str] = None) -> Tuple[List[Tuple], str]:
        """
        Query Google Code Assist for code review
        
        Args:
            prompt: The review prompt
            diff: The code diff to review
            file_path: Optional file path for context
            
        Returns:
            Tuple of (line_comments, summary)
        """
        try:
            # Build the request payload
            payload = {
                "contents": [{
                    "parts": [{
                        "text": f"{prompt}\n\nDIFF:\n{diff}"
                    }]
                }],
                "generationConfig": {
                    "temperature": 0.1,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 2048,
                },
                "safetySettings": [
                    {
                        "category": "HARM_CATEGORY_HARASSMENT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_HATE_SPEECH",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    }
                ]
            }
            
            # Make the API request with API key as query parameter
            url = f"{self.base_url}/{self.model}:generateContent?key={self.api_key}"
            headers = self._get_auth_headers()
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code != 200:
                logger.error(f"Google Code Assist API error: {response.status_code} - {response.text}")
                return [], f"Error: Google Code Assist API returned {response.status_code}"
            
            result = response.json()
            
            # Extract the response text
            if 'candidates' in result and len(result['candidates']) > 0:
                llm_response = result['candidates'][0]['content']['parts'][0]['text']
                logger.debug(f"Raw LLM response: {llm_response}")
            else:
                logger.error("No response content found in Google Code Assist response")
                return [], "Error: No response content from Google Code Assist"
            
            # Parse the response for line comments and summary
            line_comments, summary = self._parse_review_response(llm_response)
            
            logger.info(f"Google Code Assist review completed: {len(line_comments)} comments, summary: {summary[:100]}...")
            
            return line_comments, summary
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error with Google Code Assist: {e}")
            return [], f"Error: Failed to connect to Google Code Assist - {e}"
        except Exception as e:
            logger.error(f"Unexpected error with Google Code Assist: {e}")
            return [], f"Error: Unexpected error with Google Code Assist - {e}"
    
    def _parse_review_response(self, llm_response: str) -> Tuple[List[Tuple], str]:
        """
        Parse the LLM response to extract line comments and summary
        
        Args:
            llm_response: Raw response from Google Code Assist
            
        Returns:
            Tuple of (line_comments, summary)
        """
        line_comments = []
        summary = ""
        
        # Try to parse structured format first
        lines = llm_response.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('LINE ') and 'COMMENT:' in line:
                try:
                    # Format: LINE X COMMENT: [comment]
                    parts = line.split('COMMENT:', 1)
                    if len(parts) == 2:
                        line_part = parts[0].strip()
                        comment = parts[1].strip()
                        
                        # Extract line number
                        line_num_match = re.search(r'LINE (\d+)', line_part)
                        if line_num_match:
                            line_num = int(line_num_match.group(1))
                            line_comments.append((None, line_num, comment))
                        else:
                            line_comments.append((None, None, comment))
                except Exception as e:
                    logger.debug(f"Error parsing line comment: {e}")
                    continue
                    
            elif line.startswith('SUMMARY:'):
                summary = line.split('SUMMARY:', 1)[1].strip()
        
        # If no structured comments found, try to extract from free text
        if not line_comments and not summary:
            logger.debug("No structured comments found, attempting free text extraction...")
            
            # Look for security-related keywords in the response
            security_keywords = [
                'hardcoded', 'password', 'credential', 'eval', 'injection',
                'security', 'vulnerability', 'unsafe', 'dangerous', 'risk'
            ]
            
            found_issues = []
            for keyword in security_keywords:
                if keyword.lower() in llm_response.lower():
                    found_issues.append(f"Found {keyword} issue")
            
            if found_issues:
                summary = f"Potential issues detected: {', '.join(found_issues[:3])}"
                line_comments.append((None, 1, "Security review needed - check for vulnerabilities"))
        
        return line_comments, summary
    
    def test_connection(self) -> bool:
        """
        Test the connection to Google Code Assist
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            # Simple test query
            test_prompt = "Please respond with 'OK' if you can see this message."
            test_diff = "This is a test diff for connection testing."
            
            line_comments, summary = self.query_for_review(test_prompt, test_diff)
            
            if "Error:" in summary:
                logger.error(f"Google Code Assist connection test failed: {summary}")
                return False
            
            logger.info("Google Code Assist connection test successful")
            return True
            
        except Exception as e:
            logger.error(f"Google Code Assist connection test failed: {e}")
            return False


def query_google_code_assist_for_review(prompt: str, diff: str, file_path: Optional[str] = None) -> Tuple[List[Tuple], str]:
    """
    Convenience function to query Google Code Assist for code review
    
    Args:
        prompt: The review prompt
        diff: The code diff to review
        file_path: Optional file path for context
        
    Returns:
        Tuple of (line_comments, summary)
    """
    try:
        client = GoogleCodeAssistClient()
        return client.query_for_review(prompt, diff, file_path)
    except Exception as e:
        logger.error(f"Failed to initialize Google Code Assist client: {e}")
        return [], f"Error: Failed to initialize Google Code Assist client - {e}" 
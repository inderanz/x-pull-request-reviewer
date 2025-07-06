"""
Gemini CLI LLM Client for X-Pull-Request-Reviewer
Handles authentication and API calls to Gemini CLI for code review.
"""

import os
import json
import subprocess
import tempfile
import re
from typing import List, Tuple, Optional
import logging
import shutil

logger = logging.getLogger(__name__)

class GeminiCLIClient:
    """Client for Gemini CLI API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini CLI client
        
        Args:
            api_key: Gemini API key (if not provided, will try to get from environment)
        """
        self.api_key = api_key or os.environ.get('GEMINI_API_KEY')
        
        # If no API key in environment, try to get from credential manager
        if not self.api_key:
            try:
                from .credential_manager import get_credential_manager
                cm = get_credential_manager()
                self.api_key = cm.get_credential("gemini_cli", "api_key")
                if self.api_key:
                    os.environ['GEMINI_API_KEY'] = self.api_key
                    logger.info("Set GEMINI_API_KEY from credential manager")
            except Exception as e:
                logger.warning(f"Could not get API key from credential manager: {e}")
        
        self.gemini_cli_path = self._find_gemini_cli()
        
        if not self.gemini_cli_path:
            raise ValueError("Gemini CLI not found. Please install it first: npm install -g @google/gemini-cli")
        
        if not self.api_key:
            logger.warning("Gemini API key not set. Some features may not work properly.")
        else:
            logger.info("Gemini CLI client initialized with API key")
    
    def _find_gemini_cli(self) -> Optional[str]:
        """Find the Gemini CLI executable"""
        # Try common locations
        possible_paths = [
            "gemini",  # If installed globally
            shutil.which("gemini"),  # System PATH
            os.path.expanduser("~/.npm-global/bin/gemini"),  # NPM global
            os.path.expanduser("~/node_modules/.bin/gemini"),  # Local node_modules
        ]
        
        for path in possible_paths:
            if path and shutil.which(path):
                try:
                    # Test if it's working
                    result = subprocess.run([path, "--version"], 
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        logger.info(f"Found Gemini CLI at: {path}")
                        return path
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    continue
        
        return None
    
    def _run_gemini_cli(self, prompt: str, timeout: int = 60) -> str:
        """
        Run Gemini CLI with a prompt
        
        Args:
            prompt: The prompt to send to Gemini
            timeout: Timeout in seconds
            
        Returns:
            The response from Gemini CLI
        """
        try:
            # Ensure API key is set in environment
            if self.api_key:
                os.environ['GEMINI_API_KEY'] = self.api_key
            
            # Create a temporary file for the prompt
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(prompt)
                temp_file = f.name
            
            try:
                # Run Gemini CLI with the correct syntax for newer versions
                cmd = [self.gemini_cli_path, "--prompt", prompt]
                
                # Set environment variables
                env = os.environ.copy()
                if self.api_key:
                    env['GEMINI_API_KEY'] = self.api_key
                
                logger.info(f"Running Gemini CLI command: {' '.join(cmd)}")
                logger.info(f"Environment GEMINI_API_KEY set: {bool(env.get('GEMINI_API_KEY'))}")
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    env=env
                )
                
                logger.info(f"Gemini CLI exit code: {result.returncode}")
                logger.info(f"Gemini CLI stdout length: {len(result.stdout)}")
                logger.info(f"Gemini CLI stderr: {result.stderr}")
                
                if result.returncode != 0:
                    logger.error(f"Gemini CLI error: {result.stderr}")
                    return f"Error: Gemini CLI returned {result.returncode} - {result.stderr}"
                
                response = result.stdout.strip()
                logger.info(f"Gemini CLI response: {response[:200]}...")
                return response
                
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_file)
                except OSError:
                    pass
                    
        except subprocess.TimeoutExpired:
            logger.error("Gemini CLI request timed out")
            return "Error: Request timed out"
        except Exception as e:
            logger.error(f"Error running Gemini CLI: {e}")
            return f"Error: Failed to run Gemini CLI - {e}"
    
    def query_for_review(self, prompt: str, diff: str, file_path: Optional[str] = None) -> Tuple[List[Tuple], str]:
        """
        Query Gemini CLI for code review
        
        Args:
            prompt: The review prompt
            diff: The code diff to review
            file_path: Optional file path for context
            
        Returns:
            Tuple of (line_comments, summary)
        """
        try:
            # Build a more structured prompt for Gemini CLI
            structured_prompt = f"""
You are an expert security code reviewer. Analyze the following code changes and provide specific, actionable feedback.

REQUIRED OUTPUT FORMAT:
You MUST respond with EXACTLY this format - no other text:

LINE <line_number> COMMENT: <specific issue and how to fix it>
LINE <line_number> COMMENT: <specific issue and how to fix it>
...
SUMMARY: <overall assessment and priority actions>

RULES:
1. For each security issue, vulnerability, or best practice violation, use LINE <number> COMMENT: format
2. Include the actual line number from the diff where the issue occurs
3. Provide specific, actionable advice on how to fix each issue
4. End with a SUMMARY that gives an overall assessment
5. Focus on security vulnerabilities, compliance issues, and best practices
6. Be specific about what's wrong and how to fix it

EXAMPLES OF GOOD RESPONSES:
LINE 15 COMMENT: Hardcoded password detected. Replace with environment variable: DB_PASSWORD = os.environ.get('DB_PASSWORD')
LINE 23 COMMENT: SQL injection vulnerability. Use parameterized queries instead of string concatenation
LINE 45 COMMENT: Missing input validation. Add validation for user input before processing
SUMMARY: Found 3 critical security issues. Fix hardcoded credentials, SQL injection, and add input validation.

DIFF TO REVIEW:
{diff}

STATIC ANALYSIS:
{prompt}

Now provide your review in the exact format specified above. Focus on the most critical security and compliance issues.
"""
            
            logger.info(f"Sending structured review request to Gemini CLI...")
            logger.info(f"Prompt length: {len(structured_prompt)} characters")
            logger.info(f"Diff length: {len(diff)} characters")
            
            # Get response from Gemini CLI
            llm_response = self._run_gemini_cli(structured_prompt)
            
            if llm_response.startswith("Error:"):
                logger.error(f"Gemini CLI error: {llm_response}")
                return [], llm_response
            
            # Parse the response for line comments and summary
            line_comments, summary = self._parse_review_response(llm_response)
            
            logger.info(f"Gemini CLI review completed: {len(line_comments)} comments, summary: {summary[:100]}...")
            logger.info(f"Raw LLM response: {llm_response[:500]}...")
            
            return line_comments, summary
            
        except Exception as e:
            logger.error(f"Unexpected error with Gemini CLI: {e}")
            return [], f"Error: Unexpected error with Gemini CLI - {e}"
    
    def _parse_review_response(self, llm_response: str) -> Tuple[List[Tuple], str]:
        """
        Parse the LLM response to extract line comments and summary
        
        Args:
            llm_response: Raw response from Gemini CLI
            
        Returns:
            Tuple of (line_comments, summary)
        """
        line_comments = []
        summary = ""
        
        logger.info(f"Parsing LLM response: {llm_response[:200]}...")
        
        # Try to parse structured format first
        lines = llm_response.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Parse LINE comments
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
                            logger.info(f"Parsed line comment: line {line_num} - {comment[:50]}...")
                        else:
                            # If no line number found, try to extract from the line
                            line_comments.append((None, None, comment))
                            logger.info(f"Parsed comment without line number: {comment[:50]}...")
                except Exception as e:
                    logger.debug(f"Error parsing line comment: {e}")
                    continue
                    
            # Parse SUMMARY
            elif line.startswith('SUMMARY:'):
                summary = line.split('SUMMARY:', 1)[1].strip()
                logger.info(f"Parsed summary: {summary[:100]}...")
        
        # If no structured comments found, try to extract from free text
        if not line_comments and not summary:
            logger.debug("No structured comments found, attempting free text extraction...")
            
            # Look for security-related keywords and try to create comments
            security_keywords = [
                'hardcoded', 'password', 'credential', 'eval', 'injection',
                'security', 'vulnerability', 'unsafe', 'dangerous', 'risk',
                'public', 'exposed', 'unencrypted', 'weak', 'outdated'
            ]
            
            found_issues = []
            for keyword in security_keywords:
                if keyword.lower() in llm_response.lower():
                    found_issues.append(f"Found {keyword} issue")
            
            if found_issues:
                summary = f"Potential issues detected: {', '.join(found_issues[:3])}"
                line_comments.append((None, 1, "Security review needed - check for vulnerabilities"))
                logger.info(f"Created fallback comment: {summary}")
        
        # If we have a summary but no line comments, create a general comment
        if summary and not line_comments:
            line_comments.append((None, 1, f"General review: {summary[:100]}"))
            logger.info(f"Created general comment from summary")
        
        logger.info(f"Final parsing result: {len(line_comments)} comments, summary: {summary[:100]}...")
        return line_comments, summary
    
    def test_connection(self) -> bool:
        """
        Test the connection to Gemini CLI
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            # Simple test query
            test_prompt = "Please respond with 'OK' if you can see this message."
            test_diff = "This is a test diff for connection testing."
            
            line_comments, summary = self.query_for_review(test_prompt, test_diff)
            
            if "Error:" in summary:
                logger.error(f"Gemini CLI connection test failed: {summary}")
                return False
            
            logger.info("Gemini CLI connection test successful")
            return True
            
        except Exception as e:
            logger.error(f"Gemini CLI connection test failed: {e}")
            return False
    
    def install_gemini_cli(self) -> bool:
        """
        Install Gemini CLI if not already installed
        
        Returns:
            True if installation successful, False otherwise
        """
        try:
            logger.info("Installing Gemini CLI...")
            
            # Try npm install
            result = subprocess.run(
                ["npm", "install", "-g", "@google/gemini-cli"],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            if result.returncode == 0:
                logger.info("Gemini CLI installed successfully")
                # Update the path
                self.gemini_cli_path = self._find_gemini_cli()
                return True
            else:
                logger.error(f"Failed to install Gemini CLI: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("Gemini CLI installation timed out")
            return False
        except Exception as e:
            logger.error(f"Error installing Gemini CLI: {e}")
            return False


def query_gemini_cli_for_review(prompt: str, diff: str, file_path: Optional[str] = None) -> Tuple[List[Tuple], str]:
    """
    Convenience function to query Gemini CLI for code review
    
    Args:
        prompt: The review prompt
        diff: The code diff to review
        file_path: Optional file path for context
        
    Returns:
        Tuple of (line_comments, summary)
    """
    try:
        client = GeminiCLIClient()
        return client.query_for_review(prompt, diff, file_path)
    except Exception as e:
        logger.error(f"Failed to initialize Gemini CLI client: {e}")
        return [], f"Error: Failed to initialize Gemini CLI client - {e}" 
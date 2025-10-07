"""
Zoho OAuth Authentication Handler
Handles OAuth flow, token storage, and refresh for Zoho CRM API access.
"""

import os
import json
import time
import requests
import logging
from typing import Optional, Dict, Any
from urllib.parse import urlencode
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
from threading import Thread
import queue

logger = logging.getLogger(__name__)

class CallbackServer(BaseHTTPRequestHandler):
    """Simple HTTP server to handle OAuth callback."""
    
    def do_GET(self):
        """Handle GET request for OAuth callback."""
        if self.path.startswith('/callback'):
            query_params = parse_qs(urlparse(self.path).query)
            if 'code' in query_params:
                self.server.auth_code = query_params['code'][0]
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b"""
                <html>
                <body>
                    <h2>Authorization Successful!</h2>
                    <p>You can now close this window and return to your application.</p>
                    <script>window.close();</script>
                </body>
                </html>
                """)
            elif 'error' in query_params:
                self.server.auth_error = query_params['error'][0]
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b"""
                <html>
                <body>
                    <h2>Authorization Failed!</h2>
                    <p>Error: """ + query_params.get('error_description', ['Unknown error'])[0].encode() + b"""</p>
                </body>
                </html>
                """)
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Suppress default HTTP server logging."""
        pass

class ZohoAuth:
    """Handles Zoho OAuth authentication and token management."""
    
    def __init__(self, 
                 client_id: str,
                 client_secret: str,
                 redirect_uri: str,
                 scope: str,
                 token_file_path: str = ".zoho_tokens.json",
                 api_domain: str = "https://www.zohoapis.com",
                 accounts_domain: str = "https://accounts.zoho.com"):
        """Initialize Zoho authentication handler."""
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scope = scope
        self.token_file_path = token_file_path
        self.api_domain = api_domain
        self.accounts_domain = accounts_domain
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = None
        self.api_domain_for_tokens = None
        
        # Load existing tokens
        self._load_tokens()
    
    def _load_tokens(self) -> None:
        """Load tokens from file if they exist."""
        if os.path.exists(self.token_file_path):
            try:
                with open(self.token_file_path, 'r') as f:
                    tokens = json.load(f)
                    self.access_token = tokens.get('access_token')
                    self.refresh_token = tokens.get('refresh_token')
                    self.token_expires_at = tokens.get('expires_at')
                    self.api_domain_for_tokens = tokens.get('api_domain', self.api_domain)
                    logger.info("Loaded existing tokens from file")
            except Exception as e:
                logger.error(f"Failed to load tokens: {e}")
    
    def _save_tokens(self, tokens: Dict[str, Any]) -> None:
        """Save tokens to file."""
        try:
            # Calculate expiration time
            expires_at = time.time() + tokens.get('expires_in', 3600)
            
            token_data = {
                'access_token': tokens.get('access_token'),
                'refresh_token': tokens.get('refresh_token', self.refresh_token),
                'expires_at': expires_at,
                'api_domain': tokens.get('api_domain', self.api_domain_for_tokens or self.api_domain),
                'token_type': tokens.get('token_type', 'Bearer'),
                'scope': tokens.get('scope', self.scope)
            }
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.token_file_path) if os.path.dirname(self.token_file_path) else '.', exist_ok=True)
            
            with open(self.token_file_path, 'w') as f:
                json.dump(token_data, f, indent=2)
            
            # Update instance variables
            self.access_token = token_data['access_token']
            self.refresh_token = token_data['refresh_token']
            self.token_expires_at = token_data['expires_at']
            self.api_domain_for_tokens = token_data['api_domain']
            
            logger.info("Tokens saved successfully")
        except Exception as e:
            logger.error(f"Failed to save tokens: {e}")
            raise
    
    def get_authorization_url(self) -> str:
        """Generate the authorization URL for OAuth flow."""
        params = {
            'scope': self.scope,
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': self.redirect_uri,
            'access_type': 'offline',
            'prompt': 'consent'
        }
        
        auth_url = f"{self.accounts_domain}/oauth/v2/auth?{urlencode(params)}"
        return auth_url
    
    def authorize_interactive(self) -> bool:
        """Perform interactive OAuth authorization."""
        try:
            auth_url = self.get_authorization_url()
            
            print(f"\\n{'='*60}")
            print("ZOHO CRM AUTHENTICATION REQUIRED")
            print(f"{'='*60}")
            print("Opening your web browser for Zoho authentication...")
            print("If the browser doesn't open automatically, please visit:")
            print(f"{auth_url}")
            print(f"{'='*60}\\n")
            
            # Start callback server
            server = HTTPServer(('localhost', 8080), CallbackServer)
            server.auth_code = None
            server.auth_error = None
            server.timeout = 300  # 5 minutes timeout
            
            # Open browser
            webbrowser.open(auth_url)
            
            print("Waiting for authorization (timeout: 5 minutes)...")
            
            # Handle one request (the callback)
            start_time = time.time()
            while time.time() - start_time < 300:
                server.handle_request()
                if server.auth_code or server.auth_error:
                    break
            
            if server.auth_error:
                logger.error(f"Authorization failed: {server.auth_error}")
                return False
            
            if not server.auth_code:
                logger.error("Authorization timed out")
                return False
            
            # Exchange code for tokens
            return self._exchange_code_for_tokens(server.auth_code)
            
        except Exception as e:
            logger.error(f"Interactive authorization failed: {e}")
            return False
    
    def _exchange_code_for_tokens(self, auth_code: str) -> bool:
        """Exchange authorization code for access tokens."""
        try:
            token_url = f"{self.accounts_domain}/oauth/v2/token"
            
            data = {
                'grant_type': 'authorization_code',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'redirect_uri': self.redirect_uri,
                'code': auth_code
            }
            
            response = requests.post(token_url, data=data)
            
            if response.status_code == 200:
                tokens = response.json()
                self._save_tokens(tokens)
                logger.info("Successfully obtained access tokens")
                return True
            else:
                logger.error(f"Token exchange failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to exchange code for tokens: {e}")
            return False
    
    def refresh_access_token(self) -> bool:
        """Refresh the access token using refresh token."""
        if not self.refresh_token:
            logger.error("No refresh token available")
            return False
        
        try:
            token_url = f"{self.accounts_domain}/oauth/v2/token"
            
            data = {
                'grant_type': 'refresh_token',
                'refresh_token': self.refresh_token,
                'client_id': self.client_id,
                'client_secret': self.client_secret
            }
            
            response = requests.post(token_url, data=data)
            
            if response.status_code == 200:
                tokens = response.json()
                self._save_tokens(tokens)
                logger.info("Successfully refreshed access token")
                return True
            else:
                logger.error(f"Token refresh failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to refresh token: {e}")
            return False
    
    def is_token_valid(self) -> bool:
        """Check if the current access token is valid."""
        if not self.access_token or not self.token_expires_at:
            return False
        
        # Token is valid if it doesn't expire within the next 5 minutes
        return time.time() < (self.token_expires_at - 300)
    
    def get_valid_access_token(self) -> Optional[str]:
        """Get a valid access token, refreshing if necessary."""
        if self.is_token_valid():
            return self.access_token
        
        logger.info("Access token expired or invalid, attempting refresh...")
        
        if self.refresh_access_token():
            return self.access_token
        
        logger.warning("Token refresh failed, interactive authorization required")
        if self.authorize_interactive():
            return self.access_token
        
        logger.error("Failed to obtain valid access token")
        return None
    
    def get_api_domain(self) -> str:
        """Get the appropriate API domain for making requests."""
        return self.api_domain_for_tokens or self.api_domain
    
    def get_headers(self) -> Dict[str, str]:
        """Get the authorization headers for API requests."""
        token = self.get_valid_access_token()
        if not token:
            raise Exception("No valid access token available")
        
        return {
            'Authorization': f'Zoho-oauthtoken {token}',
            'Content-Type': 'application/json'
        }
    
    def revoke_tokens(self) -> bool:
        """Revoke the current tokens."""
        try:
            if self.refresh_token:
                revoke_url = f"{self.accounts_domain}/oauth/v2/token/revoke"
                data = {'token': self.refresh_token}
                response = requests.post(revoke_url, data=data)
                
                if response.status_code != 200:
                    logger.warning(f"Token revocation warning: {response.status_code} - {response.text}")
            
            # Clear tokens
            self.access_token = None
            self.refresh_token = None
            self.token_expires_at = None
            self.api_domain_for_tokens = None
            
            # Remove token file
            if os.path.exists(self.token_file_path):
                os.remove(self.token_file_path)
            
            logger.info("Tokens revoked successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to revoke tokens: {e}")
            return False
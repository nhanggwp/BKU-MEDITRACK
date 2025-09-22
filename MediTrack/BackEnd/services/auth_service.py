from supabase import create_client, Client
from jose import JWTError, jwt
from typing import Optional, Dict, Any
import httpx
from config.settings import Settings

class AuthService:
    def __init__(self):
        self.settings = Settings()
        self.client: Client = create_client(
            self.settings.supabase_url,
            self.settings.supabase_key
        )
    
    async def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token and return user data"""
        try:
            # Verify with Supabase
            response = self.client.auth.get_user(token)
            if response.user:
                return {
                    "id": response.user.id,
                    "email": response.user.email,
                    "user_metadata": response.user.user_metadata
                }
            else:
                raise Exception("Invalid token")
        except Exception as e:
            raise Exception(f"Token verification failed: {str(e)}")
    
    async def sign_up(self, email: str, password: str, user_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Sign up new user"""
        try:
            response = self.client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": user_data or {}
                }
            })
            
            if response.user:
                return {
                    "user": {
                        "id": response.user.id,
                        "email": response.user.email,
                        "email_confirmed_at": response.user.email_confirmed_at
                    },
                    "session": {
                        "access_token": response.session.access_token if response.session else None,
                        "refresh_token": response.session.refresh_token if response.session else None
                    }
                }
            else:
                raise Exception("Sign up failed")
                
        except Exception as e:
            raise Exception(f"Sign up error: {str(e)}")
    
    async def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        """Sign in user"""
        try:
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.user and response.session:
                return {
                    "user": {
                        "id": response.user.id,
                        "email": response.user.email,
                        "last_sign_in_at": response.user.last_sign_in_at
                    },
                    "session": {
                        "access_token": response.session.access_token,
                        "refresh_token": response.session.refresh_token,
                        "expires_at": response.session.expires_at
                    }
                }
            else:
                raise Exception("Invalid credentials")
                
        except Exception as e:
            raise Exception(f"Sign in error: {str(e)}")
    
    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token"""
        try:
            response = self.client.auth.refresh_session(refresh_token)
            
            if response.session:
                return {
                    "access_token": response.session.access_token,
                    "refresh_token": response.session.refresh_token,
                    "expires_at": response.session.expires_at
                }
            else:
                raise Exception("Token refresh failed")
                
        except Exception as e:
            raise Exception(f"Token refresh error: {str(e)}")
    
    async def sign_out(self, token: str) -> bool:
        """Sign out user"""
        try:
            self.client.auth.sign_out()
            return True
        except Exception as e:
            return False
    
    async def reset_password(self, email: str) -> bool:
        """Send password reset email"""
        try:
            response = self.client.auth.reset_password_email(email)
            return True
        except Exception as e:
            raise Exception(f"Password reset error: {str(e)}")
    
    async def update_password(self, refresh_token: str, new_password: str) -> bool:
        """Update user password"""
        try:
            # Set the session
            #self.client.auth.set_session(token, None)
            session = self.client.auth.refresh_session(refresh_token)
            response = self.client.auth.update_user({
                "password": new_password
            })
            return response.user is not None
        except Exception as e:
            raise Exception(f"Password update error: {str(e)}")
    
    def extract_user_id_from_token(self, token: str) -> str:
        """Extract user ID from JWT token without verification (for internal use)"""
        try:
            payload = jwt.get_unverified_claims(token)
            return payload.get("sub")
        except JWTError:
            raise Exception("Invalid token format")
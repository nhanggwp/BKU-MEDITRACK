from cryptography.fernet import Fernet
import qrcode
from qrcode.image.pil import PilImage
import base64
import json
import uuid
from typing import Dict, Any, Optional, List
from io import BytesIO
from config.settings import Settings
from services.supabase_service import SupabaseService
import datetime

class QRService:
    def __init__(self, supabase_service: SupabaseService = None):
        self.settings = Settings()
        self.supabase = supabase_service or SupabaseService()
        # Generate or use existing encryption key
        self.encryption_key = self._get_or_create_encryption_key()
        self.fernet = Fernet(self.encryption_key)
    
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key for QR codes"""
        if len(self.settings.qr_encryption_key) == 32:
            # Convert to base64 URL-safe format for Fernet
            key = base64.urlsafe_b64encode(self.settings.qr_encryption_key.encode()[:32])
            return key
        else:
            # Generate a new key if not properly configured
            return Fernet.generate_key()
    
    async def create_medical_qr(
        self, 
        user_id: str, 
        include_medical_history: bool = True,
        include_allergies: bool = True,
        include_current_medications: bool = True,
        expires_hours: int = 24,
        max_uses: int = 5
    ) -> Dict[str, Any]:
        """Create encrypted QR code with medical information"""
        
        try:
            # Gather medical data
            medical_data = await self._gather_medical_data(
                user_id, 
                include_medical_history, 
                include_allergies, 
                include_current_medications
            )
            
            # Create token
            token = str(uuid.uuid4())
            
            # Encrypt the data
            encrypted_data = self._encrypt_medical_data(medical_data)
            
            # Calculate expiration
            expires_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=expires_hours)
            
            # Save to database
            token_data = {
                "token": token,
                "encrypted_data": encrypted_data,
                "expires_at": expires_at.isoformat(),
                "max_uses": max_uses,
                "current_uses": 0
            }
            
            db_token = await self.supabase.create_qr_token(user_id, token_data)
            
            # Generate QR code
            qr_code_data = self._generate_qr_code(token)
            
            return {
                "token": token,
                "qr_code_base64": qr_code_data,
                "expires_at": expires_at.isoformat(),
                "max_uses": max_uses,
                "access_url": f"/api/qr/access/{token}",
                "medical_summary": {
                    "medications_count": len(medical_data.get("medications", [])),
                    "conditions_count": len(medical_data.get("medical_history", [])),
                    "allergies_count": len(medical_data.get("allergies", []))
                }
            }
            
        except Exception as e:
            raise Exception(f"QR creation failed: {str(e)}")
    
    async def _gather_medical_data(
        self, 
        user_id: str, 
        include_history: bool, 
        include_allergies: bool, 
        include_medications: bool
    ) -> Dict[str, Any]:
        """Gather medical data for QR code"""
        
        medical_data = {
            "user_id": user_id,
            "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "emergency_contact": None
        }
        
        # Get user basic info
        user = await self.supabase.get_user_by_id(user_id)
        if user:
            medical_data.update({
                "full_name": user.get("full_name"),
                "date_of_birth": user.get("date_of_birth"),
                "emergency_contact": user.get("emergency_contact")
            })
        
        # Get medical history
        if include_history:
            history = await self.supabase.get_medical_history(user_id)
            medical_data["medical_history"] = [
                {
                    "condition": h.get("conditions", {}).get("name", "Unknown"),
                    "severity": h.get("conditions", {}).get("severity", "unknown"),
                    "diagnosed_date": h.get("diagnosed_date"),
                    "notes": h.get("notes")
                }
                for h in history
            ]
        
        # Get allergies
        if include_allergies:
            allergies = await self.supabase.get_allergies(user_id)
            medical_data["allergies"] = [
                {
                    "allergen": a.get("allergen"),
                    "severity": a.get("severity"),
                    "reaction": a.get("reaction")
                }
                for a in allergies
            ]
        
        # Get current medications
        if include_medications:
            schedules = await self.supabase.get_medication_schedules(user_id)
            medical_data["medications"] = [
                {
                    "name": s.get("medication_name"),
                    "dosage": s.get("dosage"),
                    "frequency": s.get("frequency_per_day"),
                    "times": s.get("times_of_day"),
                    "start_date": s.get("start_date"),
                    "notes": s.get("notes")
                }
                for s in schedules
            ]
        
        return medical_data
    
    def _encrypt_medical_data(self, medical_data: Dict[str, Any]) -> str:
        """Encrypt medical data for storage"""
        try:
            json_data = json.dumps(medical_data, default=str)
            encrypted_bytes = self.fernet.encrypt(json_data.encode())
            return base64.b64encode(encrypted_bytes).decode()
        except Exception as e:
            raise Exception(f"Encryption failed: {str(e)}")
    
    def _decrypt_medical_data(self, encrypted_data: str) -> Dict[str, Any]:
        """Decrypt medical data"""
        try:
            encrypted_bytes = base64.b64decode(encrypted_data.encode())
            decrypted_bytes = self.fernet.decrypt(encrypted_bytes)
            return json.loads(decrypted_bytes.decode())
        except Exception as e:
            raise Exception(f"Decryption failed: {str(e)}")
    
    def _generate_qr_code(self, token: str) -> str:
        """Generate QR code image as base64 string"""
        try:
            # Create access URL
            access_url = f"https://your-domain.com/api/qr/access/{token}"
            
            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(access_url)
            qr.make(fit=True)
            
            # Create image
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to base64
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            return f"data:image/png;base64,{img_str}"
            
        except Exception as e:
            raise Exception(f"QR code generation failed: {str(e)}")
    
    async def access_qr_data(self, token: str, access_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """Access and decrypt QR code data"""
        try:
            # Get token from database
            token_record = await self.supabase.get_qr_token(token)
            
            if not token_record:
                raise Exception("Invalid or expired QR code")
            
            # Check expiration
            expires_at = datetime.datetime.fromisoformat(token_record["expires_at"].replace('Z', '+00:00'))
            if expires_at < datetime.datetime.now(datetime.timezone.utc):
                raise Exception("QR code has expired")
            
            # Check usage limits
            if token_record["current_uses"] >= token_record["max_uses"]:
                raise Exception("QR code usage limit exceeded")
            
            # Decrypt data
            medical_data = self._decrypt_medical_data(token_record["encrypted_data"])
            
            # Log access
            await self._log_qr_access(token_record["id"], access_info)
            
            # Update usage count
            await self._update_qr_usage(token_record["id"], token_record["current_uses"] + 1)
            
            return {
                "medical_data": medical_data,
                "access_count": token_record["current_uses"] + 1,
                "max_uses": token_record["max_uses"],
                "expires_at": token_record["expires_at"]
            }
            
        except Exception as e:
            raise Exception(f"QR access failed: {str(e)}")
    
    async def _log_qr_access(self, qr_token_id: str, access_info: Dict[str, Any]):
        """Log QR code access"""
        try:
            log_data = {
                "qr_token_id": qr_token_id,
                "accessed_by_ip": access_info.get("ip_address") if access_info else None,
                "accessed_by_user_agent": access_info.get("user_agent") if access_info else None,
                "access_location": access_info.get("location") if access_info else None
            }
            
            # Insert access log
            response = await self.supabase.client.table('qr_access_logs').insert(log_data).execute()
            
        except Exception as e:
            print(f"Error logging QR access: {e}")
    
    async def _update_qr_usage(self, qr_token_id: str, new_count: int):
        """Update QR code usage count"""
        try:
            response = await self.supabase.client.table('qr_tokens').update({
                "current_uses": new_count
            }).eq('id', qr_token_id).execute()
        except Exception as e:
            print(f"Error updating QR usage: {e}")
    
    async def revoke_qr_token(self, user_id: str, token: str) -> bool:
        """Revoke a QR token"""
        try:
            # Set expiration to now
            now = datetime.datetime.now(datetime.timezone.utc)
            response = await self.supabase.client.table('qr_tokens').update({
                "expires_at": now.isoformat()
            }).eq('token', token).eq('user_id', user_id).execute()
            
            return len(response.data) > 0
        except Exception as e:
            return False
    
    async def list_user_qr_tokens(self, user_id: str) -> List[Dict[str, Any]]:
        """List all QR tokens for a user"""
        try:
            response = await self.supabase.client.table('qr_tokens').select('''
                id, token, expires_at, max_uses, current_uses, created_at
            ''').eq('user_id', user_id).order('created_at', desc=True).execute()
            
            tokens = []
            now = datetime.datetime.now(datetime.timezone.utc)
            
            for token in response.data:
                expires_at = datetime.datetime.fromisoformat(token["expires_at"].replace('Z', '+00:00'))
                is_expired = expires_at < now
                is_used_up = token["current_uses"] >= token["max_uses"]
                
                tokens.append({
                    **token,
                    "is_active": not (is_expired or is_used_up),
                    "is_expired": is_expired,
                    "is_used_up": is_used_up
                })
            
            return tokens
        except Exception as e:
            raise Exception(f"Error fetching QR tokens: {str(e)}")
    
    async def generate_encrypted_qr(self, user_id: str, options: dict = None):
        """Generate an encrypted QR code for medical data sharing"""
        try:
            # Use the existing create_medical_qr method with default settings
            default_options = {
                "include_medical_history": True,
                "include_allergies": True, 
                "include_current_medications": True,
                "max_uses": 1,
                "expires_hours": 24
            }
            
            # Override with provided options
            if options:
                default_options.update(options)
            
            return await self.create_medical_qr(
                user_id=user_id,
                include_medical_history=default_options["include_medical_history"],
                include_allergies=default_options["include_allergies"],
                include_current_medications=default_options["include_current_medications"],
                expires_hours=default_options["expires_hours"],
                max_uses=default_options["max_uses"]
            )
        except Exception as e:
            raise Exception(f"Error generating encrypted QR: {str(e)}")

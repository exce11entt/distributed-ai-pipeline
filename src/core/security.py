import os
import re
from fastapi import Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN

# API Key Security Configuration
API_KEY_NAME = "X-API-KEY"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

def get_api_key(header_key: str = Security(api_key_header)):
    """Validates the API key from the request header."""
    expected_key = os.getenv("INTERNAL_API_KEY", "dev-secret-key") # Default for dev
    if header_key == expected_key:
        return header_key
    else:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate API Key"
        )

class SecurityService:
    @staticmethod
    def mask_pii(text: str) -> str:
        """
        Simple regex-based PII masker for demo purposes.
        In production, use a library like Presidio.
        """
        # Mask emails
        text = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '[EMAIL]', text)
        # Mask phone numbers (basic pattern)
        text = re.sub(r'\+?\d{10,12}', '[PHONE]', text)
        # Mask potential ID numbers/Credit cards
        text = re.sub(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', '[SENSITIVE_ID]', text)
        
        return text

    @staticmethod
    def validate_input(text: str) -> bool:
        """Checks for common prompt injection patterns."""
        blacklist = ["ignore all previous instructions", "system prompt", "as a developer"]
        for phrase in blacklist:
            if phrase in text.lower():
                return False
        return True

security_service = SecurityService()

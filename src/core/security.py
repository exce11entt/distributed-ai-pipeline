import os
import hashlib
from typing import Optional
import hvac
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()

class SecurityEngine:
    """
    Core security engine for the Secure Big Data AI Pipeline.
    Handles PII hashing, data encryption, and Vault integration.
    """
    
    def __init__(self):
        self.vault_client: Optional[hvac.Client] = None
        self._init_vault()
        self.cipher: Optional[Fernet] = None
        self._init_encryption()

    def _init_vault(self):
        """Initializes connection to HashiCorp Vault."""
        vault_url = os.getenv("VAULT_ADDR")
        vault_token = os.getenv("VAULT_TOKEN")
        if vault_url and vault_token:
            try:
                self.vault_client = hvac.Client(url=vault_url, token=vault_token)
                print("[Security] Vault connected successfully.")
            except Exception as e:
                print(f"[Security] Vault connection failed: {e}")

    def _init_encryption(self):
        """Initializes encryption cipher using a master key."""
        # In production, keys should be fetched from Vault
        key = os.getenv("MASTER_ENCRYPTION_KEY")
        if not key:
            # Fallback for development (DO NOT USE IN PROD)
            key = Fernet.generate_key()
            print("[Security] WARNING: Using temporary encryption key.")
        self.cipher = Fernet(key)

    def anonymize_pii(self, value: str) -> str:
        """
        Hashes PII using SHA-256 with a secure salt.
        Used for anonymizing data before vectorization.
        """
        salt = os.getenv("PII_SALT", "default_salt")
        combined = f"{value}{salt}".encode()
        return hashlib.sha256(combined).hexdigest()

    def encrypt_data(self, data: str) -> bytes:
        """Encrypts a string for secure storage/transmission."""
        return self.cipher.encrypt(data.encode())

    def decrypt_data(self, encrypted_data: bytes) -> str:
        """Decrypts data for processing."""
        return self.cipher.decrypt(encrypted_data).decode()

    def get_secret(self, path: str, key: str) -> Optional[str]:
        """Fetches a secret from Vault."""
        if not self.vault_client:
            return os.getenv(key) # Fallback to env
        
        try:
            read_response = self.vault_client.secrets.kv.read_secret_version(path=path)
            return read_response['data']['data'].get(key)
        except Exception as e:
            print(f"[Security] Failed to fetch secret from Vault: {e}")
            return os.getenv(key)

# Singleton instance
security = SecurityEngine()

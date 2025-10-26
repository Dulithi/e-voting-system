"""
Shared cryptographic utilities
All cryptographic operations follow the design document specifications:
- Curve25519 for key agreement
- Ed25519 for signatures
- AES-256-GCM for symmetric encryption
- HKDF-SHA256 for key derivation
"""

from cryptography.hazmat.primitives.asymmetric import ed25519, x25519
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305
from cryptography.hazmat.backends import default_backend
import secrets
import os
from typing import Tuple, Dict
import base64


class CryptoUtils:
    """Cryptographic utility functions"""
    
    @staticmethod
    def generate_random_bytes(length: int = 32) -> bytes:
        """
        Generate cryptographically secure random bytes
        Uses OS CSPRNG (urandom on Linux, BCryptGenRandom on Windows)
        """
        return secrets.token_bytes(length)
    
    @staticmethod
    def generate_ed25519_keypair() -> Tuple[bytes, bytes]:
        """
        Generate Ed25519 signing key pair
        Returns: (private_key_bytes, public_key_bytes)
        """
        private_key = ed25519.Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        
        private_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption()
        )
        public_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        
        return private_bytes, public_bytes
    
    @staticmethod
    def ed25519_sign(private_key_bytes: bytes, message: bytes) -> bytes:
        """
        Sign message with Ed25519
        """
        from cryptography.hazmat.primitives import serialization
        
        private_key = ed25519.Ed25519PrivateKey.from_private_bytes(private_key_bytes)
        signature = private_key.sign(message)
        return signature
    
    @staticmethod
    def ed25519_verify(public_key_bytes: bytes, message: bytes, signature: bytes) -> bool:
        """
        Verify Ed25519 signature
        """
        from cryptography.hazmat.primitives import serialization
        
        try:
            public_key = ed25519.Ed25519PublicKey.from_public_bytes(public_key_bytes)
            public_key.verify(signature, message)
            return True
        except Exception:
            return False
    
    @staticmethod
    def generate_x25519_keypair() -> Tuple[bytes, bytes]:
        """
        Generate X25519 key agreement key pair
        Returns: (private_key_bytes, public_key_bytes)
        """
        from cryptography.hazmat.primitives import serialization
        
        private_key = x25519.X25519PrivateKey.generate()
        public_key = private_key.public_key()
        
        private_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption()
        )
        public_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        
        return private_bytes, public_bytes
    
    @staticmethod
    def x25519_key_agreement(private_key_bytes: bytes, public_key_bytes: bytes) -> bytes:
        """
        Perform X25519 ECDH key agreement
        Returns shared secret
        """
        from cryptography.hazmat.primitives import serialization
        
        private_key = x25519.X25519PrivateKey.from_private_bytes(private_key_bytes)
        public_key = x25519.X25519PublicKey.from_public_bytes(public_key_bytes)
        
        shared_secret = private_key.exchange(public_key)
        return shared_secret
    
    @staticmethod
    def hkdf_derive_key(
        input_key_material: bytes,
        length: int = 32,
        salt: bytes = None,
        info: bytes = b"evoting-key-derivation"
    ) -> bytes:
        """
        HKDF-SHA256 key derivation
        """
        if salt is None:
            salt = b"\x00" * 32
        
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=length,
            salt=salt,
            info=info,
            backend=default_backend()
        )
        return hkdf.derive(input_key_material)
    
    @staticmethod
    def aes_gcm_encrypt(plaintext: bytes, key: bytes, aad: bytes = b"") -> Dict[str, bytes]:
        """
        AES-256-GCM encryption
        Returns: dict with 'ciphertext', 'nonce', 'tag'
        """
        if len(key) != 32:
            raise ValueError("AES-256 requires 32-byte key")
        
        nonce = CryptoUtils.generate_random_bytes(12)  # 96 bits
        aesgcm = AESGCM(key)
        
        # GCM combines ciphertext and tag
        ciphertext_and_tag = aesgcm.encrypt(nonce, plaintext, aad)
        
        # Separate ciphertext and tag (last 16 bytes is tag)
        ciphertext = ciphertext_and_tag[:-16]
        tag = ciphertext_and_tag[-16:]
        
        return {
            "ciphertext": ciphertext,
            "nonce": nonce,
            "tag": tag
        }
    
    @staticmethod
    def aes_gcm_decrypt(
        ciphertext: bytes,
        key: bytes,
        nonce: bytes,
        tag: bytes,
        aad: bytes = b""
    ) -> bytes:
        """
        AES-256-GCM decryption
        """
        if len(key) != 32:
            raise ValueError("AES-256 requires 32-byte key")
        
        aesgcm = AESGCM(key)
        ciphertext_and_tag = ciphertext + tag
        
        try:
            plaintext = aesgcm.decrypt(nonce, ciphertext_and_tag, aad)
            return plaintext
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")
    
    @staticmethod
    def chacha20_poly1305_encrypt(plaintext: bytes, key: bytes, aad: bytes = b"") -> Dict[str, bytes]:
        """
        ChaCha20-Poly1305 encryption (fallback for devices without AES-NI)
        """
        if len(key) != 32:
            raise ValueError("ChaCha20 requires 32-byte key")
        
        nonce = CryptoUtils.generate_random_bytes(12)  # 96 bits
        chacha = ChaCha20Poly1305(key)
        
        ciphertext_and_tag = chacha.encrypt(nonce, plaintext, aad)
        ciphertext = ciphertext_and_tag[:-16]
        tag = ciphertext_and_tag[-16:]
        
        return {
            "ciphertext": ciphertext,
            "nonce": nonce,
            "tag": tag
        }
    
    @staticmethod
    def chacha20_poly1305_decrypt(
        ciphertext: bytes,
        key: bytes,
        nonce: bytes,
        tag: bytes,
        aad: bytes = b""
    ) -> bytes:
        """
        ChaCha20-Poly1305 decryption
        """
        if len(key) != 32:
            raise ValueError("ChaCha20 requires 32-byte key")
        
        chacha = ChaCha20Poly1305(key)
        ciphertext_and_tag = ciphertext + tag
        
        try:
            plaintext = chacha.decrypt(nonce, ciphertext_and_tag, aad)
            return plaintext
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")
    
    @staticmethod
    def sha256(data: bytes) -> bytes:
        """
        SHA-256 hash
        """
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(data)
        return digest.finalize()
    
    @staticmethod
    def hmac_sha256(key: bytes, message: bytes) -> bytes:
        """
        HMAC-SHA256
        """
        h = hmac.HMAC(key, hashes.SHA256(), backend=default_backend())
        h.update(message)
        return h.finalize()
    
    @staticmethod
    def constant_time_compare(a: bytes, b: bytes) -> bool:
        """
        Constant-time comparison to prevent timing attacks
        """
        return secrets.compare_digest(a, b)


class ECIESEncryption:
    """
    Elliptic Curve Integrated Encryption Scheme
    Using X25519 + AES-256-GCM + HKDF
    """
    
    @staticmethod
    def encrypt(recipient_public_key: bytes, plaintext: bytes) -> Dict[str, bytes]:
        """
        ECIES encryption
        Returns: dict with 'ephemeral_public_key', 'ciphertext', 'nonce', 'tag'
        """
        # Generate ephemeral key pair
        ephemeral_private, ephemeral_public = CryptoUtils.generate_x25519_keypair()
        
        # Perform ECDH
        shared_secret = CryptoUtils.x25519_key_agreement(ephemeral_private, recipient_public_key)
        
        # Derive encryption key
        encryption_key = CryptoUtils.hkdf_derive_key(
            shared_secret,
            length=32,
            info=b"ecies-encryption-key"
        )
        
        # Encrypt with AES-GCM
        encrypted = CryptoUtils.aes_gcm_encrypt(plaintext, encryption_key)
        
        return {
            "ephemeral_public_key": ephemeral_public,
            "ciphertext": encrypted["ciphertext"],
            "nonce": encrypted["nonce"],
            "tag": encrypted["tag"]
        }
    
    @staticmethod
    def decrypt(
        private_key: bytes,
        ephemeral_public_key: bytes,
        ciphertext: bytes,
        nonce: bytes,
        tag: bytes
    ) -> bytes:
        """
        ECIES decryption
        """
        # Perform ECDH
        shared_secret = CryptoUtils.x25519_key_agreement(private_key, ephemeral_public_key)
        
        # Derive encryption key
        encryption_key = CryptoUtils.hkdf_derive_key(
            shared_secret,
            length=32,
            info=b"ecies-encryption-key"
        )
        
        # Decrypt with AES-GCM
        plaintext = CryptoUtils.aes_gcm_decrypt(ciphertext, encryption_key, nonce, tag)
        
        return plaintext


# Helper functions for encoding/decoding
def bytes_to_base64(data: bytes) -> str:
    """Convert bytes to base64 string"""
    return base64.b64encode(data).decode('utf-8')

def base64_to_bytes(data: str) -> bytes:
    """Convert base64 string to bytes"""
    return base64.b64decode(data)

def bytes_to_hex(data: bytes) -> str:
    """Convert bytes to hex string"""
    return data.hex()

def hex_to_bytes(data: str) -> bytes:
    """Convert hex string to bytes"""
    return bytes.fromhex(data)

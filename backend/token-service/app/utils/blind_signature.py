"""
RSA Blind Signature Implementation
Used for issuing anonymous voting credentials
"""
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
import base64


class BlindSignature:
    """RSA Blind Signature implementation for anonymous tokens"""
    
    def __init__(self, key_size: int = 2048):
        self.key_size = key_size
        self.private_key = None
        self.public_key = None
    
    def generate_keys(self):
        """Generate RSA key pair for blind signing"""
        key = RSA.generate(self.key_size)
        self.private_key = key
        self.public_key = key.publickey()
        return self.private_key, self.public_key
    
    def export_public_key(self) -> str:
        """Export public key as PEM string"""
        if not self.public_key:
            raise ValueError("No public key available")
        return self.public_key.export_key().decode('utf-8')
    
    def import_private_key(self, key_pem: str):
        """Import private key from PEM string"""
        self.private_key = RSA.import_key(key_pem.encode('utf-8'))
        self.public_key = self.private_key.publickey()
    
    def blind_sign(self, blinded_message: bytes) -> bytes:
        """
        Sign a blinded message (server-side)
        Note: In true blind signature, server signs without seeing original message
        """
        if not self.private_key:
            raise ValueError("No private key available for signing")
        
        # Convert blinded message to integer
        blinded_int = int.from_bytes(blinded_message, byteorder='big')
        
        # Sign the blinded message: s = m'^d mod n
        n = self.private_key.n
        d = self.private_key.d
        signature_int = pow(blinded_int, d, n)
        
        # Convert back to bytes
        signature_bytes = signature_int.to_bytes(
            (signature_int.bit_length() + 7) // 8, 
            byteorder='big'
        )
        
        return signature_bytes
    
    @staticmethod
    def blind_message(message: bytes, public_key: RSA.RsaKey, blinding_factor: int = None) -> tuple:
        """
        Blind a message (client-side)
        Returns (blinded_message, blinding_factor)
        """
        import secrets
        
        # Hash the message
        h = SHA256.new(message)
        message_hash = int.from_bytes(h.digest(), byteorder='big')
        
        n = public_key.n
        e = public_key.e
        
        # Generate random blinding factor if not provided
        if blinding_factor is None:
            blinding_factor = secrets.randbelow(n - 1) + 1
        
        # Compute blinded message: m' = m * r^e mod n
        blinded = (message_hash * pow(blinding_factor, e, n)) % n
        
        # Convert to bytes
        blinded_bytes = blinded.to_bytes((blinded.bit_length() + 7) // 8, byteorder='big')
        
        return blinded_bytes, blinding_factor
    
    @staticmethod
    def unblind_signature(blinded_signature: bytes, blinding_factor: int, public_key: RSA.RsaKey) -> bytes:
        """
        Unblind the signature (client-side)
        Returns unblinded signature
        """
        n = public_key.n
        
        # Convert signature to integer
        sig_int = int.from_bytes(blinded_signature, byteorder='big')
        
        # Compute modular inverse of blinding factor
        r_inv = pow(blinding_factor, -1, n)
        
        # Unblind: s = s' * r^-1 mod n
        unblinded_int = (sig_int * r_inv) % n
        
        # Convert to bytes
        unblinded_bytes = unblinded_int.to_bytes(
            (unblinded_int.bit_length() + 7) // 8,
            byteorder='big'
        )
        
        return unblinded_bytes
    
    @staticmethod
    def verify_signature(message: bytes, signature: bytes, public_key: RSA.RsaKey) -> bool:
        """
        Verify an unblinded signature (anyone can verify)
        """
        try:
            h = SHA256.new(message)
            message_hash_int = int.from_bytes(h.digest(), byteorder='big')
            sig_int = int.from_bytes(signature, byteorder='big')
            
            n = public_key.n
            e = public_key.e
            
            # Verify: m = s^e mod n
            verified_int = pow(sig_int, e, n)
            
            return verified_int == message_hash_int
        except Exception:
            return False


# Global blind signature instance (in production, load keys from secure storage)
_blind_signer = None


def get_blind_signer() -> BlindSignature:
    """Get or create the blind signature instance"""
    global _blind_signer
    if _blind_signer is None:
        _blind_signer = BlindSignature()
        # In production, load keys from environment or key management service
        # For now, generate on startup (keys will be lost on restart - acceptable for MVP)
        _blind_signer.generate_keys()
    return _blind_signer

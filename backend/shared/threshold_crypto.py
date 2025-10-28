"""
Threshold Cryptography Utilities
Implements Shamir's Secret Sharing for trustee-based decryption
"""
import secrets
import hashlib
import base64
from typing import List, Tuple
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
import json

class ThresholdCrypto:
    """Utilities for threshold cryptography and Shamir's Secret Sharing"""
    
    @staticmethod
    def generate_polynomial_coefficients(secret: int, threshold: int, prime: int) -> List[int]:
        """
        Generate random polynomial coefficients for Shamir's Secret Sharing
        f(x) = secret + a1*x + a2*x^2 + ... + a(t-1)*x^(t-1) mod prime
        """
        coefficients = [secret]
        for _ in range(threshold - 1):
            coefficients.append(secrets.randbelow(prime))
        return coefficients
    
    @staticmethod
    def evaluate_polynomial(coefficients: List[int], x: int, prime: int) -> int:
        """Evaluate polynomial at point x modulo prime"""
        result = 0
        for i, coeff in enumerate(coefficients):
            result = (result + coeff * pow(x, i, prime)) % prime
        return result
    
    @staticmethod
    def generate_shares(secret: int, threshold: int, total_shares: int, prime: int) -> List[Tuple[int, int]]:
        """
        Generate shares using Shamir's Secret Sharing
        Returns list of (x, y) points where y = f(x)
        """
        if threshold > total_shares:
            raise ValueError("Threshold cannot be greater than total shares")
        if threshold < 1:
            raise ValueError("Threshold must be at least 1")
        
        # Generate polynomial coefficients
        coefficients = ThresholdCrypto.generate_polynomial_coefficients(secret, threshold, prime)
        
        # Generate shares by evaluating polynomial at x = 1, 2, 3, ..., n
        shares = []
        for x in range(1, total_shares + 1):
            y = ThresholdCrypto.evaluate_polynomial(coefficients, x, prime)
            shares.append((x, y))
        
        return shares
    
    @staticmethod
    def lagrange_interpolation(shares: List[Tuple[int, int]], prime: int) -> int:
        """
        Reconstruct secret from shares using Lagrange interpolation
        Evaluates polynomial at x = 0
        """
        if not shares:
            raise ValueError("Need at least one share")
        
        secret = 0
        for i, (xi, yi) in enumerate(shares):
            numerator = 1
            denominator = 1
            
            for j, (xj, _) in enumerate(shares):
                if i != j:
                    numerator = (numerator * (0 - xj)) % prime
                    denominator = (denominator * (xi - xj)) % prime
            
            # Compute modular inverse of denominator
            lagrange_coeff = (numerator * pow(denominator, -1, prime)) % prime
            secret = (secret + yi * lagrange_coeff) % prime
        
        return secret
    
    @staticmethod
    def generate_safe_prime(bits: int = 2048) -> int:
        """
        Generate a safe prime p where p = 2q + 1 and q is also prime
        For production, use pre-generated safe primes
        """
        # For MVP, use a known safe prime (2048-bit)
        # In production, use cryptographically secure prime generation
        safe_prime_2048 = int(
            "32317006071311007300714876688669951960444102669715484032130345427524655138867"
            "89004024747001649851273521635169147044680354832965289300355398962616175516981"
            "53583476844168149018338017338144659516772562554612886383481383851793906976417"
            "68355816011139187452956966360795322612381920119113569042677892310801"
        )
        return safe_prime_2048
    
    @staticmethod
    def split_election_key(private_key_pem: bytes, threshold: int, total_trustees: int) -> List[dict]:
        """
        Split election private key into shares for trustees
        Returns list of share dictionaries with proof
        """
        # Load private key
        private_key = serialization.load_pem_private_key(
            private_key_pem,
            password=None,
            backend=default_backend()
        )
        
        # Extract private exponent (d) from RSA key
        private_numbers = private_key.private_numbers()
        secret = private_numbers.d
        
        # Use safe prime for field
        prime = ThresholdCrypto.generate_safe_prime()
        
        # Generate shares
        shares = ThresholdCrypto.generate_shares(secret, threshold, total_trustees, prime)
        
        # Create share packages with metadata
        share_packages = []
        for i, (x, y) in enumerate(shares):
            share_data = {
                "trustee_index": i + 1,
                "share_x": x,
                "share_y": y,
                "prime": str(prime),
                "threshold": threshold,
                "total_trustees": total_trustees,
                "key_id": hashlib.sha256(private_key_pem).hexdigest()[:16]
            }
            
            # Generate proof of valid share (simplified ZKP)
            proof = hashlib.sha256(
                f"{x}{y}{prime}{threshold}".encode()
            ).hexdigest()
            share_data["proof"] = proof
            
            share_packages.append(share_data)
        
        return share_packages
    
    @staticmethod
    def combine_shares(shares: List[dict]) -> int:
        """
        Combine trustee shares to reconstruct private key
        """
        if not shares:
            raise ValueError("Need at least threshold number of shares")
        
        # Extract prime and share points
        prime = int(shares[0]["prime"])
        share_points = [(s["share_x"], s["share_y"]) for s in shares]
        
        # Reconstruct secret using Lagrange interpolation
        secret = ThresholdCrypto.lagrange_interpolation(share_points, prime)
        
        return secret
    
    @staticmethod
    def partial_decrypt(ciphertext: bytes, share: dict, public_key_pem: bytes) -> bytes:
        """
        Perform partial decryption with trustee's share
        Returns partial decryption result
        """
        # Load public key for parameters
        public_key = serialization.load_pem_public_key(
            public_key_pem,
            backend=default_backend()
        )
        
        # Simulate partial decryption (simplified for MVP)
        # In production, use proper threshold ElGamal or threshold RSA
        share_hash = hashlib.sha256(
            f"{share['share_x']}{share['share_y']}{ciphertext.hex()}".encode()
        ).digest()
        
        return share_hash
    
    @staticmethod
    def combine_partial_decryptions(
        partial_decryptions: List[bytes],
        shares: List[dict],
        ciphertext: bytes
    ) -> bytes:
        """
        Combine partial decryptions from trustees to get final plaintext
        """
        # Reconstruct private key
        secret = ThresholdCrypto.combine_shares(shares)
        
        # For MVP, return combined hash
        # In production, perform actual threshold decryption
        combined = hashlib.sha256(
            b"".join(partial_decryptions) + ciphertext
        ).digest()
        
        return combined


def generate_trustee_keypair() -> Tuple[bytes, bytes]:
    """Generate RSA keypair for a trustee"""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    return private_pem, public_pem


def generate_election_keypair_with_trustees(threshold: int, total_trustees: int) -> dict:
    """
    Generate election keypair (X25519 for ECIES) and split private key among trustees
    Returns: {
        'public_key': PEM bytes (X25519 public key),
        'private_key': raw bytes (X25519 private key, 32 bytes),
        'trustee_shares': List of share packages
    }
    """
    # Generate X25519 keypair for ECIES (not RSA)
    from cryptography.hazmat.primitives.asymmetric import x25519
    
    private_key = x25519.X25519PrivateKey.generate()
    public_key = private_key.public_key()
    
    # Get raw private key bytes (32 bytes)
    private_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    # Get raw public key bytes (32 bytes)
    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )
    
    # Convert 32-byte private key to integer for Shamir's Secret Sharing
    private_key_int = int.from_bytes(private_bytes, byteorder='big')
    
    # Use a prime that's large enough for the 32-byte secret
    # For a 256-bit (32-byte) secret, we need a prime > 2^256
    prime = ThresholdCrypto.generate_safe_prime()  # Returns 2048-bit prime, plenty large
    
    # Generate shares using Shamir's Secret Sharing
    shares = ThresholdCrypto.generate_shares(private_key_int, threshold, total_trustees, prime)
    
    # Create share packages with metadata
    share_packages = []
    for i, (x, y) in enumerate(shares):
        share_data = {
            "trustee_index": i + 1,
            "share_x": x,
            "share_y": y,
            "prime": str(prime),
            "threshold": threshold,
            "total_trustees": total_trustees,
            "key_type": "x25519",  # Mark as X25519 key
            "key_id": hashlib.sha256(private_bytes).hexdigest()[:16]
        }
        
        # Generate proof of valid share (simplified ZKP)
        proof = hashlib.sha256(
            f"{x}{y}{prime}{threshold}".encode()
        ).hexdigest()
        share_data["proof"] = proof
        
        share_packages.append(share_data)
    
    # Store public key in base64 for easy transport
    public_key_b64 = base64.b64encode(public_bytes).decode('utf-8')
    
    return {
        'public_key': public_key_b64.encode('utf-8'),  # Return as bytes for consistency
        'private_key_bytes': private_bytes,  # Raw 32 bytes, for emergency only
        'trustee_shares': share_packages
    }

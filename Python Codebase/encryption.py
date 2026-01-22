"""
Message Encryption Module for ClassChat
Implement hybrid encryption: RSA for key exchange, AES for message encryption
"""
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
import base64


class MessageEncryption:
    """Handles RSA + AES hybrid encryption for secure communication"""

    def __init__(self):
        """Initialize encryption handler"""
        self.session_key = None  # AES session key (will be set after key exchange)
        self.rsa_private_key = None  # Server's RSA private key
        self.rsa_public_key = None  # Server's RSA public key (for client)
        self.peer_public_key = None  # Peer's public key (if needed)

    # ==================== RSA KEY MANAGEMENT ====================
    
    def generate_rsa_keys(self):
        """
        Generate RSA key pair (Server side)
        Returns: (private_key, public_key)
        """
        self.rsa_private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        self.rsa_public_key = self.rsa_private_key.public_key()
        return self.rsa_private_key, self.rsa_public_key

    def get_public_key_pem(self):
        """
        Export public key to PEM format (for transmission to client)
        Returns: Base64-encoded PEM string
        """
        if not self.rsa_public_key:
            raise ValueError("No public key available. Call generate_rsa_keys() first.")
        
        pem = self.rsa_public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return base64.b64encode(pem).decode('utf-8')

    def load_public_key_pem(self, pem_b64):
        """
        Load public key from base64-encoded PEM (Client side)
        """
        pem = base64.b64decode(pem_b64.encode('utf-8'))
        self.rsa_public_key = serialization.load_pem_public_key(
            pem,
            backend=default_backend()
        )

    # ==================== SESSION KEY (AES) MANAGEMENT ====================
    
    def generate_session_key(self):
        """
        Generate random AES-256 session key (Client side)
        Returns: 32-byte session key
        """
        self.session_key = os.urandom(32)  # 256-bit AES key
        return self.session_key

    def set_session_key(self, key):
        """
        Set the AES session key
        """
        if len(key) != 32:
            raise ValueError("Session key must be 32 bytes for AES-256")
        self.session_key = key

    def encrypt_session_key(self, session_key=None):
        """
        Encrypt session key using RSA public key (Client side)
        """
        if not self.rsa_public_key:
            raise ValueError("No public key available for encryption")
        
        key_to_encrypt = session_key or self.session_key
        if not key_to_encrypt:
            raise ValueError("No session key to encrypt")

        encrypted_key = self.rsa_public_key.encrypt(
            key_to_encrypt,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return base64.b64encode(encrypted_key).decode('utf-8')

    def decrypt_session_key(self, encrypted_key_b64):
        """
        Decrypt session key using RSA private key (Server side)
        """
        if not self.rsa_private_key:
            raise ValueError("No private key available for decryption")

        encrypted_key = base64.b64decode(encrypted_key_b64.encode('utf-8'))
        
        decrypted_key = self.rsa_private_key.decrypt(
            encrypted_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        self.session_key = decrypted_key
        return decrypted_key

    # ==================== MESSAGE ENCRYPTION (AES) ====================
    
    def encrypt_message(self, message):
        """
        Encrypt message using AES-256-CBC
        """
        if not self.session_key:
            raise ValueError("No session key set. Complete key exchange first.")

        # Convert string to bytes if needed
        if isinstance(message, str):
            message = message.encode('utf-8')

        # Generate random IV (Initialization Vector)
        iv = os.urandom(16)  # AES block size is 16 bytes

        # Pad message to AES block size (PKCS7 padding)
        padded_message = self._pad(message)

        # Create cipher and encrypt
        cipher = Cipher(
            algorithms.AES(self.session_key),
            modes.CBC(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_message) + encryptor.finalize()

        # Combine IV + ciphertext and encode to base64
        encrypted_data = iv + ciphertext
        return base64.b64encode(encrypted_data).decode('utf-8')

    def decrypt_message(self, encrypted_message):
        """
        Decrypt message using AES-256-CBC
        """
        if not self.session_key:
            raise ValueError("No session key set. Complete key exchange first.")

        # Decode from base64
        encrypted_data = base64.b64decode(encrypted_message.encode('utf-8'))

        # Extract IV and ciphertext
        iv = encrypted_data[:16]
        ciphertext = encrypted_data[16:]

        # Create cipher and decrypt
        cipher = Cipher(
            algorithms.AES(self.session_key),
            modes.CBC(iv),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        padded_message = decryptor.update(ciphertext) + decryptor.finalize()

        # Remove padding and decode to string
        message = self._unpad(padded_message)
        return message.decode('utf-8')

    # ==================== HELPER METHODS ====================
    
    def _pad(self, data):
        """
        Apply PKCS7 padding
        """
        padding_length = 16 - (len(data) % 16)
        padding = bytes([padding_length] * padding_length)
        return data + padding

    def _unpad(self, data):
        """
        Remove PKCS7 padding
        """
        padding_length = data[-1]
        return data[:-padding_length]

    # ==================== UTILITY METHODS ====================
    
    def is_ready(self):
        """
        Check if encryption is ready (session key is set)
        Returns: Boolean
        """
        return self.session_key is not None

    def reset(self):
        """Reset encryption state (for new connection)"""
        self.session_key = None
        self.rsa_private_key = None
        self.rsa_public_key = None
        self.peer_public_key = None



def encrypt(data):
    """
    Legacy encrypt function (placeholder)
    """
    return data


def decrypt(data):
    """
    Legacy decrypt function (placeholder)
    """
    return data

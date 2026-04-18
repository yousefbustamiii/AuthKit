import base64
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from server.src.app.config.settings import settings

aesgcm = AESGCM(settings.aes_key)

def encrypt(plaintext: str) -> str:
    nonce = os.urandom(12)
    plaintext_bytes = plaintext.encode("utf-8")
    ciphertext_with_tag = aesgcm.encrypt(nonce, plaintext_bytes, None)
    bundle = nonce + ciphertext_with_tag
    return base64.b64encode(bundle).decode("utf-8")
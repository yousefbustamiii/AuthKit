import base64

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from server.src.app.config.settings import settings

aesgcm = AESGCM(settings.aes_key)

def decrypt(encrypted: str) -> str:
    bundle = base64.b64decode(encrypted.encode("utf-8"))
    nonce = bundle[:12]
    ciphertext_with_tag = bundle[12:]
    plaintext_bytes = aesgcm.decrypt(nonce, ciphertext_with_tag, None)
    return plaintext_bytes.decode("utf-8")
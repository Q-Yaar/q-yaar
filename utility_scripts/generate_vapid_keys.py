#!/usr/bin/env python3
import base64
import sys

try:
    from cryptography.hazmat.primitives.asymmetric import ec
    from cryptography.hazmat.primitives import serialization
except ImportError:
    print("Error: 'cryptography' library is not installed. Please run this script using your virtual environment where 'cryptography' is installed.")
    sys.exit(1)

def generate_vapid_keys():
    private_key = ec.generate_private_key(ec.SECP256R1())
    
    priv_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    pub_bytes = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.X962,
        format=serialization.PublicFormat.UncompressedPoint
    )

    vapid_public = base64.urlsafe_b64encode(pub_bytes).decode('utf-8').strip('=')
    vapid_private = base64.urlsafe_b64encode(priv_bytes).decode('utf-8').strip('=')
    
    print("\n--- Generated VAPID Keys ---")
    print(f"VAPID_PUBLIC_KEY={vapid_public}")
    print(f"VAPID_PRIVATE_KEY={vapid_private}")
    print("----------------------------\n")

if __name__ == "__main__":
    generate_vapid_keys()

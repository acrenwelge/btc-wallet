import base64
import os

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt


def derive_fernet_key(password, salt):
    """
    Derive a Fernet key from a user-provided password and salt.
    """
    if isinstance(password, str):
        password = password.encode()

    kdf = Scrypt(salt=salt, length=32, n=2**14, r=8, p=1, backend=default_backend())

    fernet_key = kdf.derive(password)
    return fernet_key


def encrypt_seed(seed, password):
    """
    Encrypt the Bitcoin HD wallet seed using a user-provided password.
    Returns the encrypted seed and salt.
    """
    # Generate a secure random salt
    salt = os.urandom(16)

    # Derive the Fernet key from the password and salt
    fernet_key = derive_fernet_key(password, salt)

    # Create a Fernet instance with the derived key
    fernet_key = base64.urlsafe_b64encode(fernet_key)
    fernet = Fernet(fernet_key)

    # Encrypt the seed
    encrypted_seed = fernet.encrypt(seed)

    # Encode the salt in a URL-safe format
    encoded_salt = base64.urlsafe_b64encode(salt)

    return encrypted_seed, encoded_salt


def decrypt_seed(encrypted_seed, salt, password):
    """
    Decrypt the Bitcoin HD wallet seed using the provided password and salt.
    """
    # Decode the salt from the URL-safe format
    decoded_salt = base64.urlsafe_b64decode(salt)

    # Derive the Fernet key from the password and salt
    fernet_key = derive_fernet_key(password, decoded_salt)

    # Create a Fernet instance with the derived key
    fernet_key = base64.urlsafe_b64encode(fernet_key)
    fernet = Fernet(fernet_key)

    # Decrypt the seed
    decrypted_seed = fernet.decrypt(encrypted_seed)

    return decrypted_seed

from __future__ import annotations

from cryptography.fernet import Fernet, InvalidToken

from shared.config import get_settings


_fernet = Fernet(get_settings().fernet_key)


def encrypt_text(value: str) -> str:
    if not value:
        return ""
    return _fernet.encrypt(value.encode("utf-8")).decode("utf-8")


def decrypt_text(value: str) -> str:
    if not value:
        return ""
    try:
        return _fernet.decrypt(value.encode("utf-8")).decode("utf-8")
    except InvalidToken:
        return ""

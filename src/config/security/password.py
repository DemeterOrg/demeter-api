"""
Módulo responsável por hashing e verificação de senhas usando Argon2id.
"""

import re
from typing import Tuple

from passlib.context import CryptContext

from src.config.settings import settings

pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
    argon2__memory_cost=65536,
    argon2__time_cost=2,
    argon2__parallelism=4,
)


def get_password_hash(password: str) -> str:
    """
    Gera hash de senha usando Argon2id.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica se a senha em texto plano corresponde ao hash.
    """
    return pwd_context.verify(plain_password, hashed_password)


def validate_password_strength(password: str) -> Tuple[bool, str]:
    """
    Valida a força da senha com base nas configurações definidas.
    """
    if len(password) < settings.PASSWORD_MIN_LENGTH:
        return False, f"A senha deve ter no mínimo {settings.PASSWORD_MIN_LENGTH} caracteres"

    if settings.PASSWORD_REQUIRE_UPPERCASE and not re.search(r"[A-Z]", password):
        return False, "A senha deve conter ao menos uma letra maiúscula"

    if settings.PASSWORD_REQUIRE_LOWERCASE and not re.search(r"[a-z]", password):
        return False, "A senha deve conter ao menos uma letra minúscula"

    if settings.PASSWORD_REQUIRE_DIGIT and not re.search(r"\d", password):
        return False, "A senha deve conter ao menos um número"

    if settings.PASSWORD_REQUIRE_SPECIAL and not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "A senha deve conter ao menos um caractere especial (!@#$%^&*(),.?\":{}|<>)"

    return True, ""


def needs_rehash(hashed_password: str) -> bool:
    """
    Verifica se o hash precisa ser atualizado.
    """
    return pwd_context.needs_update(hashed_password)

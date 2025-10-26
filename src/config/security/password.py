"""
Módulo responsável por hashing e verificação de senhas usando Argon2id.

Este módulo implementa as melhores práticas de segurança para armazenamento
de senhas, utilizando o algoritmo Argon2id (recomendado pela OWASP).
"""

import re
from typing import Tuple

from passlib.context import CryptContext

from src.config.settings import settings

# Configuração do CryptContext com Argon2id
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
    argon2__memory_cost=65536,  # 64 MB
    argon2__time_cost=2,
    argon2__parallelism=4,
)


def get_password_hash(password: str) -> str:
    """
    Gera hash de senha usando Argon2id.

    Args:
        password: Senha em texto plano

    Returns:
        Hash da senha

    Example:
        >>> hashed = get_password_hash("MySecurePassword123!")
        >>> print(hashed)
        $argon2id$v=19$m=65536,t=2,p=4$...
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica se a senha em texto plano corresponde ao hash.

    Args:
        plain_password: Senha em texto plano fornecida pelo usuário
        hashed_password: Hash armazenado no banco de dados

    Returns:
        True se a senha corresponder, False caso contrário

    Example:
        >>> hashed = get_password_hash("MySecurePassword123!")
        >>> verify_password("MySecurePassword123!", hashed)
        True
        >>> verify_password("WrongPassword", hashed)
        False
    """
    return pwd_context.verify(plain_password, hashed_password)


def validate_password_strength(password: str) -> Tuple[bool, str]:
    """
    Valida a força da senha com base nas configurações definidas.

    Verifica:
    - Comprimento mínimo
    - Presença de letra maiúscula (se configurado)
    - Presença de letra minúscula (se configurado)
    - Presença de dígito (se configurado)
    - Presença de caractere especial (se configurado)

    Args:
        password: Senha a ser validada

    Returns:
        Tupla (is_valid, error_message):
        - is_valid: True se a senha atender todos os requisitos
        - error_message: Mensagem de erro descritiva (vazia se válida)

    Example:
        >>> is_valid, error = validate_password_strength("weak")
        >>> print(is_valid)
        False
        >>> print(error)
        A senha deve ter no mínimo 8 caracteres
    """
    # Validar comprimento mínimo
    if len(password) < settings.PASSWORD_MIN_LENGTH:
        return False, f"A senha deve ter no mínimo {settings.PASSWORD_MIN_LENGTH} caracteres"

    # Validar letra maiúscula
    if settings.PASSWORD_REQUIRE_UPPERCASE and not re.search(r"[A-Z]", password):
        return False, "A senha deve conter ao menos uma letra maiúscula"

    # Validar letra minúscula
    if settings.PASSWORD_REQUIRE_LOWERCASE and not re.search(r"[a-z]", password):
        return False, "A senha deve conter ao menos uma letra minúscula"

    # Validar dígito
    if settings.PASSWORD_REQUIRE_DIGIT and not re.search(r"\d", password):
        return False, "A senha deve conter ao menos um número"

    # Validar caractere especial
    if settings.PASSWORD_REQUIRE_SPECIAL and not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "A senha deve conter ao menos um caractere especial (!@#$%^&*(),.?\":{}|<>)"

    return True, ""


def needs_rehash(hashed_password: str) -> bool:
    """
    Verifica se o hash precisa ser atualizado.

    Útil para atualizar hashes antigos quando as configurações mudam.

    Args:
        hashed_password: Hash armazenado no banco de dados

    Returns:
        True se o hash precisar ser atualizado

    Example:
        >>> hashed = get_password_hash("password123")
        >>> needs_rehash(hashed)
        False
    """
    return pwd_context.needs_update(hashed_password)

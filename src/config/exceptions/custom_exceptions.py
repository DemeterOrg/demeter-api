"""
Exceções personalizadas da aplicação DEMETER.
"""

from typing import Any, Dict, Optional


class DemeterException(Exception):
    """
    Exceção base para todas as exceções customizadas da aplicação.
    """

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """
        Converte a exceção para um dicionário.
        """
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            "details": self.details,
        }


class AuthenticationError(DemeterException):
    """
    Exceção levantada quando a autenticação falha.
    """

    def __init__(
        self,
        message: str = "Falha na autenticação",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message=message, status_code=401, details=details)


class AuthorizationError(DemeterException):
    """
    Exceção levantada quando o usuário não tem permissão para acessar um recurso.
    """

    def __init__(
        self,
        message: str = "Acesso negado",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message=message, status_code=403, details=details)


class ValidationError(DemeterException):
    """
    Exceção levantada quando a validação de dados falha.
    """

    def __init__(
        self,
        message: str = "Erro de validação",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message=message, status_code=422, details=details)


class NotFoundError(DemeterException):
    """
    Exceção levantada quando um recurso não é encontrado.
    """

    def __init__(
        self,
        message: str = "Recurso não encontrado",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message=message, status_code=404, details=details)


class ConflictError(DemeterException):
    """
    Exceção levantada quando há conflito com o estado atual do recurso.
    """

    def __init__(
        self,
        message: str = "Conflito com recurso existente",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message=message, status_code=409, details=details)


class DatabaseError(DemeterException):
    """
    Exceção levantada quando ocorre erro de banco de dados.
    """

    def __init__(
        self,
        message: str = "Erro no banco de dados",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message=message, status_code=500, details=details)


class ExternalServiceError(DemeterException):
    """
    Exceção levantada quando há falha em serviço externo.
    """

    def __init__(
        self,
        message: str = "Erro em serviço externo",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message=message, status_code=503, details=details)


class RateLimitError(DemeterException):
    """
    Exceção levantada quando o limite de requisições é excedido.s
    """

    def __init__(
        self,
        message: str = "Limite de requisições excedido",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message=message, status_code=429, details=details)


class FileUploadError(DemeterException):
    """
    Exceção levantada quando há erro no upload de arquivo.
    """

    def __init__(
        self,
        message: str = "Erro no upload de arquivo",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message=message, status_code=400, details=details)


class TokenError(DemeterException):
    """
    Exceção levantada quando há erro relacionado a tokens.
    """

    def __init__(
        self,
        message: str = "Erro com token de autenticação",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message=message, status_code=401, details=details)

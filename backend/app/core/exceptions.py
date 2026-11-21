from typing import Any

from fastapi import status


class CostGuardException(Exception):
    """Base exception for all Cost Guard errors."""
    def __init__(self, message: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR, details: Any | None = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class AuthenticationError(CostGuardException):
    def __init__(self, message: str = "Missing or invalid authentication credentials"):
        super().__init__(message=message, status_code=status.HTTP_401_UNAUTHORIZED)


class InvalidAPIKeyError(CostGuardException):
    def __init__(self, message: str = "Invalid or inactive application API key"):
        super().__init__(message=message, status_code=status.HTTP_401_UNAUTHORIZED)


class ModelNotFoundError(CostGuardException):
    def __init__(self, model_name: str):
        super().__init__(
            message=f"Requested model '{model_name}' was not found or is inactive",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"model_name": model_name}
        )


class ProviderError(CostGuardException):
    def __init__(self, provider: str, message: str, status_code: int = status.HTTP_502_BAD_GATEWAY, details: Any | None = None):
        super().__init__(
            message=f"Provider '{provider}' error: {message}",
            status_code=status_code,
            details=details or {"provider": provider}
        )


class ProviderAuthenticationError(ProviderError):
    def __init__(self, provider: str, message: str = "Authentication failed with upstream provider"):
        super().__init__(provider=provider, message=message, status_code=status.HTTP_502_BAD_GATEWAY)


class ProviderRateLimitError(ProviderError):
    def __init__(self, provider: str, message: str = "Upstream provider rate limit exceeded"):
        super().__init__(provider=provider, message=message, status_code=status.HTTP_429_TOO_MANY_REQUESTS)


class ProviderTimeoutError(ProviderError):
    def __init__(self, provider: str, message: str = "Upstream provider request timed out"):
        super().__init__(provider=provider, message=message, status_code=status.HTTP_504_GATEWAY_TIMEOUT)


class ProviderUnavailableError(ProviderError):
    def __init__(self, provider: str, message: str = "Upstream provider is temporarily unavailable"):
        super().__init__(provider=provider, message=message, status_code=status.HTTP_503_SERVICE_UNAVAILABLE)


class BudgetExceededError(CostGuardException):
    def __init__(self, message: str = "Application budget limit exceeded"):
        super().__init__(message=message, status_code=status.HTTP_429_TOO_MANY_REQUESTS)

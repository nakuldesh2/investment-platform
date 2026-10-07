"""Custom exception classes for the application"""


class ApplicationException(Exception):
    """Base exception for all application errors"""

    def __init__(self, detail: str, status_code: int = 500):
        self.detail = detail
        self.status_code = status_code
        super().__init__(self.detail)


class InvalidRequestError(ApplicationException):
    """Raised when client request is invalid"""

    def __init__(self, detail: str):
        super().__init__(detail, 400)


class NotFoundError(ApplicationException):
    """Raised when requested resource is not found"""

    def __init__(self, detail: str = "Resource not found"):
        super().__init__(detail, 404)


class UnauthorizedError(ApplicationException):
    """Raised when user is not authenticated"""

    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(detail, 401)


class ForbiddenError(ApplicationException):
    """Raised when user lacks permission"""

    def __init__(self, detail: str = "Forbidden"):
        super().__init__(detail, 403)


class RateLimitError(ApplicationException):
    """Raised when API rate limit is exceeded"""

    def __init__(self, detail: str = "Rate limit exceeded"):
        super().__init__(detail, 429)


class UpstreamServiceError(ApplicationException):
    """Raised when upstream service is unavailable"""

    def __init__(self, detail: str = "Upstream service error"):
        super().__init__(detail, 502)


class DatabaseError(ApplicationException):
    """Raised when database operation fails"""

    def __init__(self, detail: str = "Database error"):
        super().__init__(detail, 500)

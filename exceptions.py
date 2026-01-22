class AppError(Exception):
    """Base exception for the application."""
    pass

class LoginError(AppError):
    """Raised when authentication or token extraction fails."""
    pass

class LocationChangeError(AppError):
    """Raised when switching location fails."""
    pass

class ParseError(AppError):
    """Raised when HTML parsing fails unexpectedly."""
    pass
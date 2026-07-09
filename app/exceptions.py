class PayLiteError(Exception):
    """Base exception for all PayLite domain errors."""
    def __init__(self, message: str = "An error occurred", status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)
    
class UserNotFoundError(PayLiteError):
    """Raised when a user lookup fails."""
    def __init__(self, message: str = "User not found"):
        super().__init__(message, status_code = 404)


class WalletNotFoundError(PayLiteError):
    """Raised when a wallet lookup fails."""
    def __init__(self, message: str = "Wallet not found"):
        super().__init__(message, status_code = 404)


class InsufficientFundsError(PayLiteError):
    """Raised when a wallet doesn't have enough balance."""
    def __init__(self, message: str = "Insufficient funds"):
        super().__init__(message, status_code = 400)


class DuplicateEmailError(PayLiteError):
    """Raised when trying to register with an already-used email."""
    def __init__(self, message: str = "Email already registered"):
        super().__init__(message, status_code = 409)


class InvalidTransferError(PayLiteError):
    """Raised for invalid transfer operations (self-transfer, bad amount, etc.)."""
    def __init__(self, message: str = "Invalid transfer"):
        super().__init__(message, status_code = 400)


class AuthenticationError(PayLiteError):
    """Raised for auth failures (bad credentials, expired token, etc.)."""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code = 401)

class InvalidResetTokenError(PayLiteError):
    """Raised for token failures (invalid token, expired token, already-used token, etc.)."""
    def __init__(self, message = "Invalid reset token"):
        super().__init__(message, status_code = 400)
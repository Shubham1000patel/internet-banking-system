class BankingError(Exception):
    """Base exception for banking-related errors."""
    pass


class InsufficientBalanceError(BankingError):
    pass


class InvalidAmountError(BankingError):
    pass


class AccountNotFoundError(BankingError):
    pass


class InactiveAccountError(BankingError):
    pass


class SameAccountTransferError(BankingError):
    pass
class ResourceConflictError(BankingError):
    """Raised when a resource conflicts with existing data."""
    pass
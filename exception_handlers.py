from fastapi import Request
from fastapi.responses import JSONResponse

from exceptions import (
    BankingError,
    AccountNotFoundError,
    InactiveAccountError,
    InvalidAmountError,
    InsufficientBalanceError,
    SameAccountTransferError
    
)
from exceptions import ResourceConflictError
 

def register_exception_handlers(app):

    @app.exception_handler(AccountNotFoundError)
    async def account_not_found_handler(
        request: Request,
        exc: AccountNotFoundError
    ):
        return JSONResponse(
            status_code=404,
            content={"detail": str(exc)}
        )

    @app.exception_handler(InsufficientBalanceError)
    async def insufficient_balance_handler(
        request: Request,
        exc: InsufficientBalanceError
    ):
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)}
        )

    @app.exception_handler(InvalidAmountError)
    async def invalid_amount_handler(
        request: Request,
        exc: InvalidAmountError
    ):
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)}
        )

    @app.exception_handler(InactiveAccountError)
    async def inactive_account_handler(
        request: Request,
        exc: InactiveAccountError
    ):
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)}
        )

    @app.exception_handler(SameAccountTransferError)
    async def same_account_handler(
        request: Request,
        exc: SameAccountTransferError
    ):
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)}
        )

    @app.exception_handler(ResourceConflictError)
    async def resource_conflict_handler(
        request: Request,
        exc: ResourceConflictError):
        return JSONResponse(
        status_code=409,
        content={"detail": str(exc)})

    @app.exception_handler(BankingError)
    async def banking_error_handler(
        request: Request,
        exc: BankingError
    ):
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)}
        )

    @app.exception_handler(Exception)
    async def unexpected_error_handler(
        request: Request,
        exc: Exception
    ):
        return JSONResponse(
            status_code=500,
            content={
                "detail": "An unexpected server error occurred."
            }
        )


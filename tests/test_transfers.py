
import json
from decimal import Decimal
from unittest.mock import MagicMock

from services.account_service import AccountService


def test_duplicate_transfer_returns_saved_response(monkeypatch):
    service = AccountService()

    connection = MagicMock()

    monkeypatch.setattr(
        "services.account_service.create_connection",
        lambda: connection
    )

    saved_response = {
        "message": "Money transferred successfully.",
        "transaction_id": 25,
        "from_account": "TEST001",
        "to_account": "TEST002",
        "amount": "100.00",
        "balance": "400.00"
    }

    service.idempotency_repository.get_by_customer_and_key = (
        MagicMock(return_value=(
            1,
            "matching-request-hash",
            json.dumps(saved_response),
            "COMPLETED"
        ))
    )

    service.idempotency_repository.create_key = MagicMock()

    # Use a stable hash for the same request.
    import hashlib

    request_data = {
        "from_account": "TEST001",
        "to_account": "TEST002",
        "amount": "100.00"
    }

    expected_hash = hashlib.sha256(
        json.dumps(request_data, sort_keys=True).encode("utf-8")
    ).hexdigest()

    service.idempotency_repository.get_by_customer_and_key.return_value = (
        1,
        expected_hash,
        json.dumps(saved_response),
        "COMPLETED"
    )
    service.account_repository.update_balance = MagicMock()
    result = service.transfer_money(
        customer_id=1,
        from_account_number="TEST001",
        to_account_number="TEST002",
        amount=Decimal("100.00"),
        idempotency_key="transfer-test-duplicate"
    )

    assert result["transaction_id"] == 25
    assert result["from_account"] == "TEST001"
    assert result["to_account"] == "TEST002"

    service.account_repository.update_balance.assert_not_called()
    service.idempotency_repository.create_key.assert_not_called()
    connection.commit.assert_not_called()
    connection.close.assert_called_once()


def test_same_idempotency_key_with_different_amount_is_rejected(monkeypatch):
    from decimal import Decimal
    from unittest.mock import MagicMock
    import hashlib
    import json
    import pytest

    from services.account_service import AccountService
    from exceptions import BankingError

    service = AccountService()
    connection = MagicMock()

    monkeypatch.setattr(
        "services.account_service.create_connection",
        lambda: connection
    )

    # The saved hash represents the original ₹100 request.
    original_request = {
        "from_account": "TEST001",
        "to_account": "TEST002",
        "amount": "100.00"
    }

    original_hash = hashlib.sha256(
        json.dumps(
            original_request,
            sort_keys=True
        ).encode("utf-8")
    ).hexdigest()

    service.idempotency_repository.get_by_customer_and_key = MagicMock(
        return_value=(
            1,
            original_hash,
            json.dumps({"transaction_id": 25}),
            "COMPLETED"
        )
    )

    with pytest.raises(BankingError):
        service.transfer_money(
            customer_id=1,
            from_account_number="TEST001",
            to_account_number="TEST002",
            amount=Decimal("500.00"),
            idempotency_key="transfer-test-duplicate"
        )

    service.account_repository.update_balance = MagicMock()
    service.account_repository.update_balance.assert_not_called()
    connection.rollback.assert_called_once()
    connection.close.assert_called_once()    
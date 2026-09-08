from concurrent.futures import ThreadPoolExecutor
from datetime import date
from decimal import Decimal
from threading import Barrier

import pytest
from django.db import close_old_connections, connection
from rest_framework.exceptions import NotFound

from finance.models import Transaction, Transfer, Wallet
from finance.models.choices import CategoryType
from finance.services.transaction_service import TransactionService
from finance.services.transfer_service import TransferService
from tests.factories import CategoryFactory, WalletFactory

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture(autouse=True)
def require_postgresql():
    if connection.vendor != "postgresql":
        pytest.skip("Row-locking tests require PostgreSQL.")


def run_concurrently(*operations):
    barrier = Barrier(len(operations))

    def run(operation):
        close_old_connections()
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT pg_backend_pid()")
                backend_pid = cursor.fetchone()[0]

            result = operation(barrier)
            return backend_pid, result, None
        except Exception as exc:
            return backend_pid, None, exc
        finally:
            close_old_connections()

    with ThreadPoolExecutor(max_workers=len(operations)) as executor:
        futures = [executor.submit(run, operation) for operation in operations]
        results = [future.result(timeout=15) for future in futures]

    assert len({backend_pid for backend_pid, _, _ in results}) == len(operations)
    return results


def update_transaction(transaction_id, validated_data):
    def operation(barrier):
        stale_transaction = Transaction.objects.select_related(
            "wallet",
            "category",
        ).get(id=transaction_id)
        barrier.wait(timeout=5)
        return TransactionService.update(
            instance=stale_transaction,
            validated_data=validated_data,
        )

    return operation


def delete_transaction(transaction_id):
    def operation(barrier):
        stale_transaction = Transaction.objects.select_related(
            "wallet",
            "category",
        ).get(id=transaction_id)
        barrier.wait(timeout=5)
        TransactionService.destroy(instance=stale_transaction)

    return operation


def create_transfer(from_wallet_id, to_wallet_id, amount):
    def operation(barrier):
        from_wallet = Wallet.objects.get(id=from_wallet_id)
        to_wallet = Wallet.objects.get(id=to_wallet_id)
        barrier.wait(timeout=5)
        return TransferService.create(
            validated_data={
                "from_wallet": from_wallet,
                "to_wallet": to_wallet,
                "amount": amount,
                "description": "Concurrent transfer",
                "transfer_date": date.today(),
            }
        )

    return operation


def test_concurrent_updates_keep_wallet_balance_consistent():
    wallet = WalletFactory(balance=Decimal("100.00"))
    category = CategoryFactory(user=wallet.user, type=CategoryType.INCOME)
    transaction = Transaction.objects.create(
        wallet=wallet,
        category=category,
        amount=Decimal("100.00"),
    )

    results = run_concurrently(
        update_transaction(transaction.id, {"amount": Decimal("150.00")}),
        update_transaction(transaction.id, {"amount": Decimal("200.00")}),
    )

    errors = [error for _, _, error in results if error is not None]
    assert errors == []
    wallet.refresh_from_db()
    transaction.refresh_from_db()
    assert wallet.balance == transaction.amount


def test_concurrent_update_and_delete_keep_wallet_balance_consistent():
    wallet = WalletFactory(balance=Decimal("100.00"))
    category = CategoryFactory(user=wallet.user, type=CategoryType.EXPENSE)
    transaction = Transaction.objects.create(
        wallet=wallet,
        category=category,
        amount=Decimal("100.00"),
    )

    results = run_concurrently(
        update_transaction(transaction.id, {"amount": Decimal("50.00")}),
        delete_transaction(transaction.id),
    )

    errors = [error for _, _, error in results if error is not None]
    assert all(isinstance(error, NotFound) for error in errors)
    wallet.refresh_from_db()
    assert not Transaction.objects.filter(id=transaction.id).exists()
    assert wallet.balance == Decimal("200.00")


def test_concurrent_deletes_reverse_transaction_only_once():
    wallet = WalletFactory(balance=Decimal("100.00"))
    category = CategoryFactory(user=wallet.user, type=CategoryType.EXPENSE)
    transaction = Transaction.objects.create(
        wallet=wallet,
        category=category,
        amount=Decimal("100.00"),
    )
    transaction_id = transaction.id

    results = run_concurrently(
        delete_transaction(transaction_id),
        delete_transaction(transaction_id),
    )

    errors = [error for _, _, error in results if error is not None]
    assert len(errors) == 1
    assert isinstance(errors[0], NotFound)
    wallet.refresh_from_db()
    assert not Transaction.objects.filter(id=transaction_id).exists()
    assert wallet.balance == Decimal("200.00")


def test_opposite_transaction_moves_do_not_deadlock():
    first_wallet = WalletFactory(balance=Decimal("100.00"))
    second_wallet = WalletFactory(user=first_wallet.user, balance=Decimal("100.00"))
    category = CategoryFactory(
        user=first_wallet.user,
        type=CategoryType.INCOME,
    )
    first_transaction = Transaction.objects.create(
        wallet=first_wallet,
        category=category,
        amount=Decimal("100.00"),
    )
    second_transaction = Transaction.objects.create(
        wallet=second_wallet,
        category=category,
        amount=Decimal("100.00"),
    )

    results = run_concurrently(
        update_transaction(first_transaction.id, {"wallet": second_wallet}),
        update_transaction(second_transaction.id, {"wallet": first_wallet}),
    )

    errors = [error for _, _, error in results if error is not None]
    assert errors == []
    first_wallet.refresh_from_db()
    second_wallet.refresh_from_db()
    assert first_wallet.balance == Decimal("100.00")
    assert second_wallet.balance == Decimal("100.00")


def test_opposite_transfers_do_not_deadlock_or_change_total_balance():
    first_wallet = WalletFactory(balance=Decimal("100.00"))
    second_wallet = WalletFactory(user=first_wallet.user, balance=Decimal("100.00"))

    results = run_concurrently(
        create_transfer(first_wallet.id, second_wallet.id, Decimal("10.00")),
        create_transfer(second_wallet.id, first_wallet.id, Decimal("20.00")),
    )

    errors = [error for _, _, error in results if error is not None]
    assert errors == []
    first_wallet.refresh_from_db()
    second_wallet.refresh_from_db()
    assert Transfer.objects.count() == 2
    assert first_wallet.balance == Decimal("110.00")
    assert second_wallet.balance == Decimal("90.00")
    assert first_wallet.balance + second_wallet.balance == Decimal("200.00")

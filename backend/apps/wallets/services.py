from django.db import transaction
from apps.wallets.models import Wallet, WalletTransaction


@transaction.atomic
def charge_credit(*, wallet_id, message, amount):
    if amount <= 0:
        raise ValueError("Deduction amount must be greater than 0")

    wallet = Wallet.objects.select_for_update().get(id=wallet_id)

    already_charged = WalletTransaction.objects.filter(
        wallet=wallet_id, transaction_type="debit", message=message
    ).exists()

    if already_charged:
        raise ValueError("Credit is already charged for this message.")

    if wallet.balance < amount:
        raise ValueError("You don't have enough credits")

    wallet.balance -= amount
    wallet.save(update_fields=["balance", "updated_at"])

    WalletTransaction.objects.create(
        wallet=wallet, amount=amount, transaction_type="debit", message=message
    )

    return wallet.balance


@transaction.atomic
def refund_credit(*, wallet_id, message):

    wallet = Wallet.objects.select_for_update().get(id=wallet_id)

    debit = WalletTransaction.objects.filter(
        wallet=wallet, message=message, transaction_type="debit"
    ).first()

    if debit is None:
        raise ValueError("Credits have not been deducted for this message")

    already_refunded = WalletTransaction.objects.filter(
        wallet=wallet_id, transaction_type="refund", message=message
    ).exists()

    if already_refunded:
        return wallet.balance

    wallet.balance += debit.amount
    wallet.save(update_fields=["balance", "updated_at"])

    WalletTransaction.objects.create(
        wallet=wallet, amount=debit.amount, transaction_type="refund", message=message
    )

    return wallet.balance

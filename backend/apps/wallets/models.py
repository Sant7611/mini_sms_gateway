from django.db import models


class Wallet(models.Model):
    user = models.OneToOneField(
        "accounts.User", on_delete=models.PROTECT, related_name="wallet"
    )
    balance = models.PositiveIntegerField(default=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {self.balance} credits"


class WalletTransaction(models.Model):

    class TransactionType(models.TextChoices):
        DEBIT = "debit", "Debit"
        REFUND = "refund", "Refund"

    wallet = models.ForeignKey(
        "wallets.Wallet", on_delete=models.PROTECT, related_name="transactions"
    )
    amount = models.PositiveIntegerField()
    transaction_type = models.CharField(max_length=20, choices=TransactionType.choices)
    message = models.ForeignKey(
        "smsmessages.SMSMessage", on_delete=models.PROTECT, related_name="transactions"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["message", "transaction_type"],
                name="unique_transaction_per_message",
            )
        ]

    def __str__(self):
        return f"{self.transaction_type} - {self.amount} credits"

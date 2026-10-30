from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class SmsProvider(models.Model):
    name = models.CharField(max_length=100, unique=True)
    priority = models.PositiveIntegerField(default=1)
    balance = models.PositiveIntegerField(default=0)
    failure_rate = models.FloatField(
        default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    error_message = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

    def getBalance(self):
        return self.balance


class ProviderAttempt(models.Model):

    class Status(models.TextChoices):
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"
        PENDING = "pending", "Pending"

    provider = models.ForeignKey(
        SmsProvider, on_delete=models.PROTECT, related_name="attempts"
    )
    message = models.ForeignKey(
        "smsmessages.SMSMessage", on_delete=models.PROTECT, related_name="attempts"
    )
    attempted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["message", "provider"], name="one_attempt_per_route"
            )
        ]

    def __str__(self):
        return f"{self.message} - {self.status} - {self.provider}"

from apps.providers.models import SmsProvider, ProviderAttempt
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q, Count
import random


def get_available_providers(parts):
    return SmsProvider.objects.filter(balance__gte=parts).order_by("priority")


@transaction.atomic
def attempt_send(*, provider_id, message):
    provider = SmsProvider.objects.select_for_update().get(id=provider_id)

    previous_attempt = ProviderAttempt.objects.filter(
        provider=provider, message=message
    ).first()

    if previous_attempt is not None:
        return previous_attempt.status == ProviderAttempt.Status.SUCCESS

    if provider.balance < message.parts:
        return False

    successful = random.random() >= provider.failure_rate

    if successful:
        provider.balance -= message.parts
        provider.save(update_fields=["balance"])

    ProviderAttempt.objects.create(
        provider=provider,
        message=message,
        status=(
            ProviderAttempt.Status.SUCCESS
            if successful
            else ProviderAttempt.Status.FAILED
        ),
    )

    return successful


def send_with_failover(*, message):
    already_sent = ProviderAttempt.objects.filter(
        message=message, status=ProviderAttempt.Status.SUCCESS
    ).exists()

    if already_sent:
        return True

    providers = get_available_providers(message.parts)

    for provider in providers:
        successful = attempt_send(provider_id=provider.id, message=message)

        if successful:
            return True

    return False


def health_check(provider):
    since = timezone.now() - timedelta(hours=24)

    attempts = ProviderAttempt.objects.filter(
        creted_at__gte=since, provider=provider, status__in=["success", "failed"]
    )
    stats = attempts.aggregate(
        total_attempts=Count("id"),
        successful=Count("id", filter=Q(status="success")),
    )
    total_attempts = stats["total_attempts"]
    successful = stats["successful"]

    balance = provider.balance

    balance_score = min(balance, 100)

    success_rate = (successful / total_attempts * 100) if total_attempts > 0 else None

    effective_rate = (
        success_rate if success_rate is not None else (1 - provider.failure_rate) * 100
    )

    health = (
        0
        if provider.balance == 0
        else round(0.8 * effective_rate + 0.2 * balance_score)
    )

    return {
        "provider": provider.name,
        "balance": balance,
        "attempts_24h": total_attempts,
        "success_rate_24h": success_rate,
        "health": health,
    }

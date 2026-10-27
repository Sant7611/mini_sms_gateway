from apps.providers.models import SmsProvider, ProviderAttempt
from django.db import transaction
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
        message=message,
        status=ProviderAttempt.Status.SUCCESS
    ).exists()

    if already_sent:
        return True

    providers = get_available_providers(message.parts)

    for provider in providers:
        successful = attempt_send(
            provider_id=provider.id,
            message=message
        )

        if successful:
            return True

    return False

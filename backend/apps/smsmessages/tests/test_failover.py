import pytest
from django.contrib.auth import get_user_model
from apps.providers.models import SmsProvider, ProviderAttempt
from apps.providers.services import send_with_failover
from apps.smsmessages.models import SMSMessage


@pytest.fixture
def sms(db):
    User = get_user_model()

    user = User.objects.create_user(
        username="test_user",
        phone_number="9841234567",
        password="TestPassword123!",
    )

    return SMSMessage.objects.create(
        sender=user,
        recipient="9801122334",
        content="A" * 200,
        parts=2,
        cost=2,
    )


@pytest.mark.django_db
def test_provider_failover(sms):
    route_a = SmsProvider.objects.create(
        name="ROUTE_A",
        priority=1,
        balance=10,
        failure_rate=1.0,
    )

    route_b = SmsProvider.objects.create(
        name="ROUTE_B",
        priority=2,
        balance=10,
        failure_rate=0.0,
    )

    result = send_with_failover(message=sms)

    assert result is True

    assert ProviderAttempt.objects.filter(
        message=sms,
        provider=route_a,
        status="failed",
    ).exists()

    assert ProviderAttempt.objects.filter(
        message=sms,
        provider=route_b,
        status="success",
    ).exists()

    route_a.refresh_from_db()
    route_b.refresh_from_db()

    assert route_a.balance == 10
    assert route_b.balance == 8


from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from django.contrib.auth import get_user_model
from django.db import close_old_connections, connections
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken
from apps.wallets.models import Wallet
from apps.providers.models import SmsProvider
from apps.smsmessages.models import SMSMessage
import pytest
@pytest.mark.django_db(transaction=True)
def test_20_concurrent_sms_requests():

    User = get_user_model()

    user = User.objects.create_user(
        username="test_concurrent",
        password="TestPassword123!",
        phone_number="9801234567",
    )

    wallet, _ = Wallet.objects.update_or_create(user=user, defaults={"balance": 10})

    SmsProvider.objects.create(
        name="ROUTE_A",
        priority=1,
        balance=100,
        failure_rate=0.0,
    )

    token = str(AccessToken.for_user(user))

    barrier = Barrier(20)

    def send_request(_):
        close_old_connections()

        try:
            client = APIClient()
            client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

            # All 20 threads start their requests together
            barrier.wait(timeout=15)

            response = client.post(
                "/api/v1/sms/send/",
                {
                    "to": ["9841234567"],
                    "message": "Hello",
                },
                format="json",
            )

            return response.status_code

        finally:
            connections.close_all()

    with ThreadPoolExecutor(max_workers=20) as executor:
        results = list(executor.map(send_request, range(20)))

    successful = sum(200 <= status < 300 for status in results)

    rejected = sum(status in (400, 402) for status in results)

    wallet.refresh_from_db()

    assert successful == 10
    assert rejected == 10
    assert wallet.balance == 0

    assert SMSMessage.objects.filter(sender=user, status="sent").count() == 10

from django.db import transaction

from apps.smsmessages.models import SMSMessage
from apps.smsmessages.utils import calculate_sms_cost
from apps.wallets.models import Wallet
from apps.wallets.services import charge_credit, refund_credit
from apps.providers.services import send_with_failover



def send_sms(*, user, recipients, content):

    cost_data = calculate_sms_cost(
        message=content,
        recipients=recipients,
    )
    
    total_cost = cost_data['total_cost']

    with transaction.atomic():
        wallet = Wallet.objects.select_for_update().get(user=user)
        
        if wallet.balance < total_cost:
            raise ValueError("Insufficient wallet balance")

        messages = []
        for recipient in recipients:

            message = SMSMessage.objects.create(
                sender=user,
                recipient=recipient,
                content=content,
                parts=cost_data["parts"],
                cost=cost_data["cost_per_recipient"],
                status=SMSMessage.Status.PENDING,
            )

            charge_credit(
                wallet_id=wallet.id,
                message=message,
                amount=message.cost,
            )

            messages.append(message)

    for message in messages:

        successful = send_with_failover(message=message)

        if successful:
            message.status = SMSMessage.Status.SENT

        else:
            with transaction.atomic():
                refund_credit(
                    wallet_id=wallet.id,
                    message=message,
                )

                message.status = SMSMessage.Status.FAILED

        message.save(update_fields=["status", "updated_at"])

    return messages

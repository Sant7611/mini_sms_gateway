from rest_framework.generics import CreateAPIView
from apps.smsmessages.serializers import SendSMSSerializer
from rest_framework.permissions import IsAuthenticated
from apps.smsmessages.models import SMSMessage
from apps.smsmessages.services import send_sms
from rest_framework.response import Response
from rest_framework import status


class SendSMSView(CreateAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = SendSMSSerializer

    def create(self, validated_data):
        user = self.request.user

        message = validated_data["message"]
        recipients = validated_data["to"]

        messages = send_sms(user=user, recipients=recipients, message=message)

        total_cost = sum(msg.cost for msg in messages)

        refunded = sum(
            msg.cost for msg in messages if msg.status == SMSMessage.Status.FAILED
        )

        return Response(
            {
                "message": message,
                "total_cost": total_cost,
                "charged_credits": total_cost - refunded,
                "refunded_credits": refunded,
                "recipients": [
                    {"phone": msg.recipient, "status": msg.status} for msg in messages
                ],
            },
            status=status.HTTP_201_CREATED,
        )

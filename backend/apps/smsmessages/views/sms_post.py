from rest_framework.generics import CreateAPIView
from apps.smsmessages.serializers import SendSMSSerializer
from rest_framework.permissions import IsAuthenticated
from apps.smsmessages.models import SMSMessage
from apps.smsmessages.services import send_sms
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from rest_framework import status


class SendSMSView(CreateAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = SendSMSSerializer

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = self.request.user
        data = serializer.validated_data

        message = data["message"]
        recipients = data["to"]

        try:
            messages = send_sms(user=user, recipients=recipients, content=message)
        except ValueError as error:
            raise ValidationError({"detail": str(error)})

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

from rest_framework import serializers
from apps.smsmessages.utils import normalize_phone
from apps.smsmessages.models import SMSMessage


class SendSMSSerializer(serializers.Serializer):
    to = serializers.ListField(child=serializers.CharField(), allow_empty=False)

    message = serializers.CharField()

    def validate_to(self, recipients):

        normalized_recipients = []

        for recipient in recipients:
            try:
                normalized = normalize_phone(recipient)

            except ValueError as error:
                raise serializers.ValidationError(str(error))

            normalized_recipients.append(normalized)

        return normalized_recipients

    def validate_message(self, message):
        if not message.strip():
            raise serializers.ValidationError("Empty message is not allowed")

        return message


class SMSReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = SMSMessage
        fields = (
            "recipient",
            "content",
            "status",
            "parts",
            "cost",
            "created_at",
        )
        read_only_fields = fields


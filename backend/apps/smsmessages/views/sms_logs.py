
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from apps.smsmessages.models import SMSMessage
from apps.smsmessages.serializers import SMSReadSerializer


class SMSLogsView(ListAPIView):
    serializer_class = SMSReadSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SMSMessage.objects.filter(
            sender=self.request.user
        ).order_by("-created_at")

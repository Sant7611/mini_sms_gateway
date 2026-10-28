
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from apps.smsmessages.pagination import SMSLogsPagination
from apps.smsmessages.models import SMSMessage
from apps.smsmessages.serializers import SMSReadSerializer
from apps.smsmessages.filters import SMSLogFilter
from django_filters.rest_framework import DjangoFilterBackend


class SMSLogsView(ListAPIView):
    serializer_class = SMSReadSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = SMSLogsPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = SMSLogFilter

    def get_queryset(self):
        return SMSMessage.objects.filter(
            sender=self.request.user
        ).order_by("-created_at")

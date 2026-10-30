
from django_filters import rest_framework as filters
from apps.smsmessages.models import SMSMessage


class SMSLogFilter(filters.FilterSet):
    date = filters.DateFilter(
        field_name="created_at",
        lookup_expr="date"
    )

    number = filters.CharFilter(
        field_name="recipient",
        lookup_expr="exact"
    )

    class Meta:
        model = SMSMessage
        fields = ["status", "date", "number"]

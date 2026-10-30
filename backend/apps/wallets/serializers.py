from rest_framework.serializers import ModelSerializer
from apps.wallets.models import WalletTransaction


class WalletTransactionSerializer(ModelSerializer):
    class Meta:
        model = WalletTransaction
        fields = (
            "id",
            "wallet",
            "amount",
            "transaction_type",
            "description",
            "created_at",
        )
        read_only_fields = fields
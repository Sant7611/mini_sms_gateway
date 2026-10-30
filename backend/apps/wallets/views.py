from rest_framework.generics import ListAPIView
from apps.wallets.serializers import WalletTransactionSerializer
from backend.apps.wallets.models import WalletTransaction

class WalletTransactionListView(ListAPIView):


    serializer_class = WalletTransactionSerializer

    def get_queryset(self):
        user = self.request.user
        return WalletTransaction.objects.filter(wallet__user=user).order_by('-created_at')
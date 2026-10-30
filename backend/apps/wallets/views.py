from rest_framework.generics import ListAPIView
from apps.wallets.serializers import WalletTransactionSerializer
from apps.wallets.models import WalletTransaction
from rest_framework.permissions import IsAuthenticated

class WalletTransactionListView(ListAPIView):


    serializer_class = WalletTransactionSerializer
    permission_classes = [IsAuthenticated]  
    def get_queryset(self):
        user = self.request.user
        return WalletTransaction.objects.filter(wallet__user=user).order_by('-created_at')
from django.urls import path
from apps.wallets.views import WalletTransactionListView

urlpatterns = [
    path('transactions/', WalletTransactionListView.as_view(), name='wallet-transaction-list'),
]
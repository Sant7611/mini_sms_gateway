from django.urls import path
from apps.accounts.views import login_view, register_view


urlpatterns = [
    path('register/', register_view.RegisterView.as_view(), name='register'),
    path('login/', login_view.LoginView.as_view(), name='login'),
]

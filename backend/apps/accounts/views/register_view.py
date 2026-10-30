from rest_framework.generics import CreateAPIView
from apps.accounts.serializers import RegistrationSerializer
from rest_framework.permissions import AllowAny


class RegisterView(CreateAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = [AllowAny]
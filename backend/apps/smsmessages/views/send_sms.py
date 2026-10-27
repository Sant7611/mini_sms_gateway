from rest_framework.generics import CreateAPIView
from apps.smsmessages.serializers import SendSMSSerializer
from rest_framework.permissions import IsAuthenticated


class SendSMSView(CreateAPIView):
    
    permission_classes = [IsAuthenticated]
    serializer_class = SendSMSSerializer
    
    
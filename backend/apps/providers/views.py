from rest_framework.views import APIView
from apps.providers.services import health_check
from apps.providers.models import SmsProvider
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class HealthView(APIView):
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        providers = SmsProvider.objects.all()
        
        data = [health_check(provider) for provider in providers]
        
        return Response(data, status=status.HTTP_200_OK)
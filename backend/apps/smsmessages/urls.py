from django.urls import path
from apps.smsmessages.views import sms_post, sms_logs


urlpatterns = [
    path('send/', sms_post.SendSMSView.as_view(), name='send_sms'),
    path('logs/', sms_logs.SMSLogsView.as_view(), name='sms_logs')
]

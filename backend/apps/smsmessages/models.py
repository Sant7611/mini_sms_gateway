from django.db import models
from django.conf import settings

class SMSMessage(models.Model):
    
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SENT = "sent", "Sent"
        FAILED = "failed", "Failed"
        
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='sent_messages')
    recipient = models.CharField(max_length=10)
    content = models.TextField()
    parts = models.PositiveIntegerField()
    cost = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"SMSMessage from {self.sender.email} to {self.recipient} - Status: {self.status}"
    

from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):

    phone_number = models.CharField(max_length=10, unique=True)


    REQUIRED_FIELDS = ["phone_number"]

    def __str__(self):
        return self.username

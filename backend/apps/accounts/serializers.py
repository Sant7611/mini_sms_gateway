from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from apps.wallets.models import Wallet
from django.core.exceptions import ValidationError as DjangoValidationError
from django.contrib.auth import authenticate
import re

User = get_user_model()


class RegistrationSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True, trim_whitespace=False)
    password2 = serializers.CharField(write_only=True, trim_whitespace=False)
    phone_number = serializers.CharField(
        max_length=14, write_only=True, trim_whitespace=True
    )

    class Meta:
        model = User
        fields = ["username", "password", "password2", "phone_number"]

    def validate_phone_number(self, value):

        pattern = r"(?:\+977|977)?(9[78][0-9]{8})"
        match = re.fullmatch(pattern, value.strip())

        if not match:
            raise serializers.ValidationError("Invalid Phone Number")

        phone = match.group(1)

        if User.objects.filter(phone_number=phone).exists():
            raise serializers.ValidationError("Phone number is already registered")

        return phone

    def validate(self, attrs):
        password = attrs["password"]
        password2 = attrs.pop("password2")

        if password != password2:
            raise serializers.ValidationError("Password doesn't match")

        try:
            user = User(username=attrs["username"], phone_number=attrs["phone_number"])
            validate_password(password, user=user)

        except DjangoValidationError as error:
            raise serializers.ValidationError({"password": error.messages})

        return attrs

    def create(self, validated_data):
        with transaction.atomic():
            user = User.objects.create_user(**validated_data)
            Wallet.objects.create(user=user)

        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate(self, attrs):
        username=attrs['username']
        password=attrs['password']
        user = authenticate(request = self.context.get('request'), username=username, password=password)
        
        if user is None:
            raise serializers.ValidationError("Invalid Username or Password")
        
        attrs['user'] = user
        
        return attrs
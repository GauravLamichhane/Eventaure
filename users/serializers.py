from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers
from .models import CustomUser



class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only = True)
    first_name = serializers.CharField(max_length = 150)
    last_name = serializers.CharField(max_length = 150)

    class Meta:
        model = CustomUser
        fields = ["id", "first_name", "last_name", "email", "password","confirm_password"]
        read_only_fields = ["id"]
    
    def validate_email(self, value):
        normalized = value.strip().lower()
        if CustomUser.objects.filter(email = normalized).exists():
            raise serializers.ValidationError("A User with this email already exists.")
        return normalized
    
    def validate_password(self, value):
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value
    
    def validate(self, attrs):
        if attrs.get("password") != attrs.get("confirm_password"):
            raise serializers.ValidationError({"confirm_password": "Passwords do not match"})
        return attrs

    def create(self, validated_data):
        validated_data.pop("confirm_password")
        return CustomUser.objects.create_user(**validated_data)


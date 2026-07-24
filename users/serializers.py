from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):

     password = serializers.CharField(
         write_only = True,
         validators = [validate_password]

    )

     class Meta:

         model = User

         fields = [
          "username",
          "email",
          "password"
        ]

     def validate_email(self, value):
         if User.objects.filter(email=value).exists():
             raise serializers.ValidationError(
                 "User with this email already exists."
             )

         return value

     def create(self,validated_data):

         user = User.objects.create_user(
             **validated_data
         )

         return user
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import RegisterSerializer



class RegisterView(CreateAPIView):

    serializer_class = RegisterSerializer


    def create(self,request,*args,**kwargs):

        serializer = self.get_serializer(
            data = request.data
        )

        serializer.is_valid(
            raise_exception = True
        )

        user = serializer.save()

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "user": {
                    "username": user.username,
                    "email": user.email,
                },
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
            },
            status=status.HTTP_201_CREATED,
        )



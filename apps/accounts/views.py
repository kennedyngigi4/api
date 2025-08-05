from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import update_last_login
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail

from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.accounts.models import User
from apps.accounts.serializers import RegistrationSerializer, ProfileSerializer, CustomTokenObtainPairSerializer
from apps.accounts.redis import RedisJWTAuthentication
# Create your views here.



class RegistrationView(generics.CreateAPIView):
    serializer_class = RegistrationSerializer
    queryset = User.objects.all()

    def post(self, request, *args, **kwargs):
        try: 
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({ "status": status.HTTP_201_CREATED, "success": True })
            else:
                return Response({ "status": status.HTTP_406_NOT_ACCEPTABLE, "success": False })
            
            
        except:
            return Response({ "status": status.HTTP_500_INTERNAL_SERVER_ERROR, "success": False })


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            data = response.data

            # update last login
            email = request.data.get("email")
            if email:
                user = get_user_model()
                user = User.objects.filter(email=email).first()
                if user:
                    update_last_login(None, user)

            return Response(data, status=status.HTTP_200_OK)
        
        except AuthenticationFailed as e:
            return Response({ "error", str(e) })
        except Exception as e:
            return Response({"error": "An unexpected error occurred.", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LogoutView(APIView):
    permission_classes = [ IsAuthenticated ]
    
    def post(self, request):
        auth_header = request.header.get("Authorization")
        if auth_header and auth_header.startswith("Token "):
            token = auth_header.split(" ")[1]
            RedisJWTAuthentication.deleteToken(token)

        return Response({ "message": "Logged out successfully"}, status=200)
    
   


class ProfileView(APIView):
    permission_classes = [ IsAuthenticated ]
    serializer_class = ProfileSerializer
    queryset = User.objects.all()

    def get(self, request, *args, **kwargs):
        user = self.request.user
        queryset = User.objects.get(uid=user.uid)
        return Response(ProfileSerializer(queryset).data)




class ForgotPasswordAPIView(APIView):
    def post(self, request):
        email = request.data.get("email")

        try:
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.uid))
            token = default_token_generator.make_token(user)
            reset_url = f"https://kenautos.co.ke/reset-password/{uid}/{token}/"

            send_mail(
                subject="Reset your password",
                message=f"Click the link to reset your password: {reset_url}",
                from_email="hello@kenautos.co.ke",
                recipient_list=[email]
            )

            return Response({ "success": True, "message": "Password reset email sent."})

        except User.DoesNotExist:
            return Response({ "success": False, "message": "User not found"}, status=status.HTTP_404_NOT_FOUND)



class ResetPasswordView(APIView):
    def post(self, request):
        uidb64 = request.data.get("uid")
        token = request.data.get("token")

        new_password = request.data.get("new_password")
        
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(uid=uid)

            if default_token_generator.check_token(user, token):
                user.set_password(new_password)
                user.save()
                return Response({ "success":True, "message": "Password has been reset"})
            else:
                return Response({ "success":False, "message": "Invalid or Expired token" }, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({ "success":False, "message": "Invalid request" }, status=status.HTTP_400_BAD_REQUEST)




from django.urls import path
from apps.accounts.views import LoginView, RegistrationView, LogoutView, ProfileView, ForgotPasswordAPIView, ResetPasswordView
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path("register/", RegistrationView.as_view(), name="register", ),
    path("login/", LoginView.as_view(), name="token_obtain_pair"),
    path("refresh/", TokenRefreshView.as_view(), name="refresh", ),
    path("logout/", LogoutView.as_view(), name="logout", ),
    path("profile/", ProfileView.as_view(), name="profile", ),
    path("forgot-password/", ForgotPasswordAPIView.as_view(), name="forgot-password", ),
    path("reset-password/", ResetPasswordView.as_view(), name="reset-password", ),
]




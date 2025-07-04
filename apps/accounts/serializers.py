from rest_framework import serializers
from apps.accounts.models import User, UserBusiness, Package
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import AuthenticationFailed
from apps.accounts.redis import RedisJWTAuthentication



class PackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        fields = "__all__"


class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBusiness
        fields = [
            "id", "name", "email", "phone", "website", "address", "latlng", "image", "banner", "facebook", 
            "instagram", "tiktok", "twitter", "youtube", "linkedin"
        ]


class ProfileSerializer(serializers.ModelSerializer):
    business = BusinessSerializer(required=True)

    class Meta:
        model = User
        fields = [
            'uid','email', 'name', 'phone', 'gender', 'image', 'date_joined', 'last_login', 'is_verified', 'is_partner', 'business' 
        ]



class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        extra_kwargs = { "write_only": { "password": True }}
        fields = [
            'email', 'name', 'phone', 'password'
        ]

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data["email"],
            phone=validated_data["phone"],
            name=validated_data["name"],
            password=validated_data["password"],
        )

        return user



class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        try:
            data = super().validate(attrs)
        except AuthenticationFailed as e:
            raise AuthenticationFailed({ "error", str(e)})
        

        # Store accessToken in redis
        user = self.user
        access_token = data["access"]
        data["success"] = True
        data["id"] = self.user.uid
        data["name"] = self.user.name
        data["email"] = self.user.email
        data["phone"] = self.user.phone
        data["is_partner"] = self.user.is_partner
        data["is_verified"] = self.user.is_verified

        RedisJWTAuthentication.storeToken(user, access_token)
        return data



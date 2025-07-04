import redis
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from apps.accounts.models import User


# Connect to redis
redis_client = redis.StrictRedis(host='127.0.0.1', port=6379, db=1, decode_responses=True)



class RedisJWTAuthentication(BaseAuthentication):
    def authentication(self, request):
        auth_header = request.header.get("Authorization")

        if not auth_header or not auth_header.startswith("Token "):
            return None
        
        token = auth_header.split(' ')[1]

        # check if token is in redis
        user_id = redis_client.get(f"token:{token}")
        if not user_id:
            raise AuthenticationFailed("Invalid or expired token")
        

        try:
            user = User.objects.get(uid=user_id)
            return (user, token)
        except User.DoesNotExist:
            raise AuthenticationFailed("User not found")
        
    
    @staticmethod
    def storeToken(user, token):
        """Store token in redis with expiration time"""
        redis_client.setex(f"token:{token}", 3600, str(user.uid)) #token expires in 1hour


    @staticmethod
    def deleteToken(token):
        """Remove token from redis for logout"""
        redis_client.delete(f"token:{token}")


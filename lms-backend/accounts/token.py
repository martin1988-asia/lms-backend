from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        data["id"] = user.id
        data["username"] = user.username
        data["email"] = user.email
        data["role"] = user.role  # assuming CustomUser has a 'role' field
        data["is_staff"] = user.is_staff
        data["is_superuser"] = user.is_superuser
        return data

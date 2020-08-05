from tokens.token import KarmenRefreshToken
from datetime import timedelta
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainSerializer
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.state import User

class KarmenTokenObtainPairSerializer(TokenObtainSerializer):
    username_field = User.USERNAME_FIELD
    lifetime = serializers.IntegerField(label='Token lifetime in seconds.', required=False, default=None)

    @classmethod
    def get_token(cls, user):
        return KarmenRefreshToken.for_user(user)

    def validate_lifetime(self, value):
        if value is None:
            return
        elif value <= 0:
            raise serializers.ValidationError("Positive number expected.")
        else:
            return timedelta(seconds=value)

    def validate(self, attrs):
        data = super().validate(attrs)

        refresh = self.get_token(self.user)
        data['refresh'] = str(refresh)

        access = refresh.access_token
        if attrs['lifetime'] is not None:
            access.set_exp(from_time=refresh.current_time, lifetime=attrs['lifetime'])
        data['access'] = str(access)

        return data


class KarmenTokenRefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        refresh = KarmenRefreshToken(attrs['refresh'])


        data = {'access': str(refresh.access_token)}

        if api_settings.ROTATE_REFRESH_TOKENS:
            if api_settings.BLACKLIST_AFTER_ROTATION:
                try:
                    # Attempt to blacklist the given refresh token
                    refresh.blacklist()
                except AttributeError:
                    # If blacklist app not installed, `blacklist` method will
                    # not be present
                    pass

            refresh.set_jti()
            refresh.set_exp()

            data['refresh'] = str(refresh)

        return data

from rest_framework.response import Response
from rest_framework import status, viewsets, decorators, permissions
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from tokens.serializers import KarmenTokenObtainPairSerializer, KarmenTokenRefreshSerializer
from users.serializers import UserSerializer
from users.models import  User


class TokensViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    def _create(self, serializer_class, request):
        '''
        creates a token based on request.data using serializer_class
        '''
        serializer = serializer_class(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        user = User(pk=serializer.user.pk)
        groups = []
        for i in serializer.user.printer_groups.all():
            d = i.__dict__
            print(d)
            d.pop("_state")
            d["uuid"] = d.pop("id")
            groups.append(d)

        request.user = serializer.user
        user_serializer = UserSerializer(context={"request":request}, instance=serializer.user)
        return Response({**user_serializer.data, **serializer.validated_data,
                         "groups":groups})
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

    def create(self, request):
        '''
        Returns fresh pair of access and refresh tokens
        '''
        return self._create(KarmenTokenObtainPairSerializer, request)

    @decorators.action(detail=False, methods=['post'])
    def refresh(self, request, *args, **kwargs):
        '''
        Returns new access and refresh token from current refresh token.
        '''
        return self._create(KarmenTokenRefreshSerializer, request)

    @decorators.action(detail=False, methods=['delete'])
    def mine(self, request):
        '''
        Destroy active token.
        '''
        request.auth.blacklist()
        return Response(status=status.HTTP_204_NO_CONTENT)

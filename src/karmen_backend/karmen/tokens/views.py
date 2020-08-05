from rest_framework.response import Response
from rest_framework import status, viewsets, decorators, permissions
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from tokens.serializers import KarmenTokenObtainPairSerializer, KarmenTokenRefreshSerializer


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

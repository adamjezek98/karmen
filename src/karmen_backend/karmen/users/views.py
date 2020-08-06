from rest_framework import serializers, viewsets, permissions, exceptions, status, decorators
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import Token
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from users.models import User
from users.serializers import InvitationRequestSerializer, ActivationRequestSerializer, UserSerializer, PasswordChangeSerializer
from karmen.permissions import IsManagerOfObject, IsUserOfObject



class InvitationsViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]
    http_method_names = ('post',)

    def create(self, request):
        if not request.user.is_anonymous:
            raise exceptions.ValidationError({
                'code': 'logged-in',
                "detail": 'You are already logged'
            }, 400)

        invitation = InvitationRequestSerializer(data=request.data)
        invitation.is_valid(raise_exception=True)
        invitation.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UsersViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'create':
            permission_classes = [permissions.AllowAny]
        elif self.action and self.action in ('me', 'me_patch'):
            permission_classes = [permissions.IsAuthenticated]
        elif self.action and self.action == 'retrieve':
            permission_classes = [permissions.IsAdminUser|IsUserOfObject]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]

    def create(self, request):
        if request.user.has_perm('add_user'):
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        elif request.user.is_authenticated:
            raise exceptions.ValidationError({
                'code': 'logged-in',
                'detail': 'You are already logged in.'
            }, 400)
        else:
            activation_request = ActivationRequestSerializer(data=request.data)
            try:
                activation_request.is_valid(raise_exception=True)
            except TokenError:
                raise InvalidToken({
                    'code': 'invalid-invitation',
                    'token': 'The token is not valid.'
                    }, 400)
            activation_request.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, pk=None):
        if not request.user.has_perm('delete_user'):
            raise exceptions.PermissionDenied()
        if pk is None:
            raise exceptions.ValidationError({'code': 'missing-id', 'detail': 'Missing primary key'})
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:  # pylint: disable=no-member
            raise exceptions.NotFound({'user': f'The user {pk} does not exist.'})
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @decorators.action(detail=False, methods=['get'])
    def me(self, request):
        user = User.objects.get(pk=request.user.pk)

        serializer = self.get_serializer(instance=user)
        print(serializer)
        print(dir(serializer))
        return Response(serializer.data)

    @me.mapping.patch
    def me_patch(self, request):
        user = User.objects.get(pk=request.user.pk)
        serializer = PasswordChangeSerializer(instance=user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

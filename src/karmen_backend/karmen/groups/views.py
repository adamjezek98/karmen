from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from rest_framework import viewsets, exceptions, status, permissions, decorators
from karmen.permissions import IsManagerOfObject, IsUserOfObject, IsUserOfParentObject, IsManagerOfParentObject
from karmen.viewsets import ObjectLevelAccessRestrictionViewSetMixin, NestedViewMixin
from users.models import User
from groups import models, serializers


class GroupsViewSet(ObjectLevelAccessRestrictionViewSetMixin, viewsets.ModelViewSet):
    '''
    Main printer group endpoint

    Only admin can list, access to individual objects depends on `group.can_*` model methods.
    '''

    serializer_class = serializers.GroupSerializer
    queryset = models.Group.objects.all()

    create_permissions = [permissions.IsAuthenticated]


class MyGroupsViewSet(GroupsViewSet):
    '''
    Same as GroupsViewSet but limited to gropus of current user.
    '''

    listing_permissions = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.request.user.printer_groups.all()


class UsersInGroupViewSet(NestedViewMixin, ObjectLevelAccessRestrictionViewSetMixin, viewsets.ModelViewSet):
    '''
    List / delete / update groups this printer belongs to.

    User listing is limited to users who can view parent object.

    Users can be added / deleted by username to make things easier
    '''

    serializer_class = serializers.UserInGroupSerializer
    lookup_field = 'user__username'
    lookup_url_kwarg = 'username'
    lookup_value_regex = '[^/]+'  # users are referenced by username which is e-mail
    parent_model = models.Group
    listing_permissions = [IsUserOfParentObject]
    create_permissions = [IsUserOfParentObject]

    def get_queryset(self):
        return models.UserInGroup.objects.filter(group=self.request.parent_instance)

    def get_permissions(self):

        if self.request.method == 'GET':
            permission_classes = [IsUserOfParentObject|IsUserOfObject]
        else:
            permission_classes = [IsManagerOfParentObject|IsManagerOfObject]
        return [permission() for permission in permission_classes]

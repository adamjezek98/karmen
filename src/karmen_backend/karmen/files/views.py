from django.shortcuts import render
from rest_framework import viewsets, permissions
from karmen.viewsets import ObjectLevelAccessRestrictionViewSetMixin, NestedViewMixin
from karmen.permissions import IsUserOfObject, IsManagerOfObject, IsUserOfParentObject, IsManagerOfParentObject
from files import models, serializers

class FilesViewSet(ObjectLevelAccessRestrictionViewSetMixin, viewsets.ModelViewSet):
    '''
    Main file group endpoint

    Only admin can list, access to individual objects depends on `group.can_*` model methods.
    '''

    serializer_class = serializers.FileSerializer
    queryset = models.File.objects.all()


class MyFilesViewSet(FilesViewSet):

    listing_permissions = create_permissions = [permissions.IsAuthenticated]

    def get_queryset(self):
        return models.File.for_user(self.request.user)


class FilesInGroupViewSet(NestedViewMixin, ObjectLevelAccessRestrictionViewSetMixin, viewsets.ModelViewSet):
    '''
    List / delete / update printers under a group endpoint.
    '''
    serializer_class = serializers.FilesInGroupSerializer
    parent_model = 'models.Group'
    listing_permissions = [IsUserOfParentObject]
    create_permissions = [IsManagerOfParentObject]

    def get_queryset(self):
        return models.File.objects.filter(group=self.request.parent_instance)

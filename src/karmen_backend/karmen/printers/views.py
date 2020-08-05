from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from rest_framework import viewsets, exceptions, status, permissions, decorators
from karmen.viewsets import ObjectLevelAccessRestrictionViewSetMixin, NestedViewMixin
from users.models import User
from printers import models, serializers
from karmen.permissions import IsManagerOfObject, IsUserOfObject, IsUserOfParentObject, IsManagerOfParentObject


class PrintersViewSet(ObjectLevelAccessRestrictionViewSetMixin, viewsets.ModelViewSet):
    '''General model view set for printers.

    Only Admin can list all printers.
    User can view / modify only printer he / she has access to (directly or through a group).
    '''

    serializer_class = serializers.PrinterSerializer
    queryset = models.Printer.objects

    create_permissions = [permissions.IsAuthenticated]



class MyPrintersViewSet(PrintersViewSet):
    '''
    Printers on currently logged in user.

    Same as General priters viewset but limited to printers of logged in user.
    Any authenticated user can list (his/her printers).
    '''

    listing_permissions = [IsUserOfObject]

    def get_queryset(self):
        return models.Printer.for_user(self.request.user)



class UsersOnPrinterViewSet(NestedViewMixin, ObjectLevelAccessRestrictionViewSetMixin, viewsets.ModelViewSet):
    '''
    List / delete / update users assigned to printer.

    User can be added to printer by username, to make things easier.
    '''

    serializer_class = serializers.UserOnPrinterSerializer
    lookup_field = 'user__username'
    lookup_url_kwarg = 'username'
    lookup_value_regex = '[^/]+'  # users are referenced by username which is e-mail
    parent_model = models.Printer  # this list is limited to a Printer
    listing_permissions = [IsUserOfParentObject]
    create_permissions = [IsManagerOfParentObject]

    def get_queryset(self):
        return models.UserOnPrinter.objects.filter(printer=self.request.parent_instance)



class PrinterGroupsViewSet(NestedViewMixin, ObjectLevelAccessRestrictionViewSetMixin, viewsets.ModelViewSet):
    '''
    Lives under printer endpoint.
    List / delete / update groups the printer belongs to.
    '''

    serializer_class = serializers.GroupsOnPrinterSerializer
    lookup_field = 'group__id'
    lookup_url_kwarg = 'group_id'
    parent_model = models.Printer
    listing_permissions = create_permissions = [IsUserOfParentObject]

    def get_queryset(self):
        return models.PrinterInGroup.objects.filter(printer=self.request.parent_instance)


class PrintersInGroupViewSet(NestedViewMixin, ObjectLevelAccessRestrictionViewSetMixin, viewsets.ModelViewSet):
    '''
    Lives under group endpoint.

    List / delete / update printers under a group endpoint.
    '''
    serializer_class = serializers.PrinterInGroupSerializer
    lookup_field = 'printer__id'
    lookup_url_kwarg = 'printer_id'
    parent_model = 'groups.Group'
    listing_permissions = [IsUserOfParentObject]
    create_permissions = [IsManagerOfParentObject&IsManagerOfObject]

    def get_queryset(self):
        return models.PrinterInGroup.objects.filter(group=self.request.parent_instance)



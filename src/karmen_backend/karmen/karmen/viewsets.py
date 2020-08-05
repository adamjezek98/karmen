from django.shortcuts import get_object_or_404
from django.apps import apps
from rest_framework import permissions
from karmen.utils import classproperty
from karmen.permissions import IsUserOfObject, IsManagerOfObject, IsUserOfParentObject


class ObjectLevelAccessRestrictionViewSetMixin(object):
    '''
    Sets permission based on users and groups assigned to printer for default ModelViewSet actions:

    list create retrieve update partial_update destroy
    '''

    listing_permissions = [permissions.IsAdminUser]
    create_permissions = [permissions.IsAdminUser]

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        # list create retrieve update partial_update destroy
        if self.action == 'list':
            permission_classes = self.listing_permissions
        elif self.action == 'create':
            permission_classes = self.create_permissions
        elif self.action in ['retrieve'] or self.request.method == 'get':
            permission_classes = [IsUserOfObject]
        elif self.action in ('create', 'update', 'partial_update', 'destroy'):
            permission_classes = [IsManagerOfObject]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]


class NestedViewMixin(object):
    '''
    Mixin for nested ViewSets .. 

    Resolves `parent_model` instance from url using kwarg
    `url_kwarg_for_parent` (defaults to `<parent_model>_id`).

    Set `url_kwarg_for_parent` descendant class to specify the kwark holding lookup
    for parent object (defaults to `<attr_name_for_parent>_id`)

    Takes parent_instance from url kwarg and
    - sets `self.parent_instance` property pointing to instance resolved from url 
    - adds the parent to serializer context under <attr_name_for_parent>
    '''

    '''parent instance attribute name'''

    url_kwarg_for_parent = None
    '''url kwarg used to lookup for parent instance'''


    parent_model = None
    '''db model representing parent ModeViewSet. Can be model instance or string'''

    def dispatch(self, request, *args, **kwargs):
        request.parent_instance = self._get_parent_instance()
        return super().dispatch(request, *args, **kwargs)

    @classmethod
    def get_parent_model(cls):
        '''resolves `parent_model` which can be model instance as well as
        string'''
        if not hasattr(cls, '_parent_model'):
            if isinstance(cls.parent_model, str):
                parent_model = apps.get_model(cls.parent_model)
            else:
                parent_model = cls.parent_model
            setattr(cls, '_parent_model', parent_model)
        return cls._parent_model

    @classmethod
    def get_parent_model_name(cls):
        if not hasattr(cls, '__attr_name_for_parent'):
            name = cls.get_parent_model()._meta.model_name
            setattr(cls, '__attr_name_for_parent', name)
        return getattr(cls, '__attr_name_for_parent')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        parent_instance = self.request.parent_instance
        context.update({
            self.get_parent_model_name(): parent_instance,
            'parent_instance': parent_instance,
        })
        return context

    def _get_parent_instance(self):
        kwarg = self.url_kwarg_for_parent
        if kwarg is None:
            kwargs = '%s_id' % self.get_parent_model_name()
        return get_object_or_404(self.get_parent_model(), pk=self.kwargs['%s_id' % self.get_parent_model_name()])

    def get_permissions(self):
        if self.request.parent_instance.can_view(self.request.user):
            return super().get_permissions()
        else:
            return [permissions.IsAdminUser()]




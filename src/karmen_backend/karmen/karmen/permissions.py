from rest_framework import permissions


class IsManagerOfObject(permissions.BasePermission):
    '''
    Allow list access to any user, object access is limited to managers.

    This permission expects that the object has `can_modify` method which
    returns `True` for user with write access.
    '''

    def has_permission(self, request, view=None):
        return request.user.is_authenticated  # and request.user.has_perm('view_printers')

    def has_object_permission(self, request, view, obj):
        if request.method == 'DELETE' and hasattr(obj, 'can_delete'):
            return obj.can_delete(request.user)
        else:
            return obj.can_modify(request.user)


class IsUserOfObject(permissions.BasePermission):
    '''
    Allows list accoss to any users, object access is limited to users assigned to the object as `can_view`.

    This permission expects that the object has `can_view` method which
    returns `True` for user with read access.
    '''

    def has_permission(self, request, view=None):
        return request.user.is_authenticated  # and request.user.has_perm('view_printers')

    def has_object_permission(self, request, view, obj):
        return obj.can_view(request.user)


class IsUserOfParentObject(permissions.BasePermission):
    '''
    Allows list accoss to any users, object access is limited to users assigned to the object as `can_view`.

    This permission expects that the object has `can_view` method which
    returns `True` for user with read access.
    '''

    def has_permission(self, request, view=None):
        return request.parent_instance.can_view(request.user)  # and request.user.has_perm('view_printers')


class IsManagerOfParentObject(permissions.BasePermission):
    '''
    Allows list accoss to any users, object access is limited to users assigned to the object as `can_view`.

    This permission expects that the object has `can_view` method which
    returns `True` for user with read access.
    '''

    def has_permission(self, request, view=None):
        return request.parent_instance.can_modify(request.user)  # and request.user.has_perm('view_printers')

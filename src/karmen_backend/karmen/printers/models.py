from django.db import models
from karmen import ROLE_ADMIN, ROLE_USER, ROLES
from karmen.models import IdField
from users.models import User


class Printer(models.Model):
    '''
    Printer registered in Karmen

    This model represents the connection setup of the print as well as user access.

    The communication to the actual device should be stored elsewhere (octoprint module for instance).
    This model should not contain cached informations from a device or it's
    current state as these informations should be cached in Django's cache
    framework only.
    '''

    id = IdField()
    name = models.CharField('Name', max_length=255, help_text="Printer will be presented by this name.")
    token = models.CharField(
        'Device token', max_length=255,
        help_text='Printer most either associated with a pill device or issued by a key manager')
    api_key = models.CharField('API key', max_length=255, blank=True, help_text='API key used to access the printer')
    users = models.ManyToManyField(User, through='UserOnPrinter', related_name='printers')
    groups = models.ManyToManyField('groups.Group', related_name='printers', through='PrinterInGroup')

    created_on = models.DateTimeField(auto_now_add=True)
    last_updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '%s (%s)' % (self.name, self.id)

    @classmethod
    def for_user(cls, user):
        'queryset of printers accessible by user `user`'
        return cls.objects.filter(
            models.Q(useronprinter__user=user) | \
            models.Q(groups__users=user)
        ).distinct()

    def list_own_users(self, role=None):
        '''
        Queryset with users directly attached to the printer (optionally) with a particular role

        If you want to include users from groups as well, use `list_users` method.
        '''
        users = User.objects.filter(useronprinter__printer=self)
        if role:
            users = users.filter(useronprinter__role=role)
        return users

    def list_users(self, role=None):
        '''queryset with users with access to the printer
           The queryset can be filtered to include only users with a specific `role`
        '''
        if role:
            users = User.objects.filter(
                models.Q(useringroup__role=role, useringroup__group__printers=self) | \
                models.Q(useronprinter__role=role, useronprinter__printer=self)
            ).distinct()
        else:
            users = User.objects.filter(
                models.Q(
                    useringroup__group__printers=self) | \
                    models.Q(printers=self)
                ).distinct()
        return users

    def has_user(self, user, role=None):
        '''
        returns True if the user has access to the printer (directly or
        throught a group) and optionally the user has specified role
        '''
        if role:
            users = self.list_users(role=role)
        else:
            users = self.list_users()
        return users.filter(pk=user.pk).exists()

    def is_admin(self, user):
        '''returns True if the user is admin (directly or through a group)'''
        return self.has_user(user, role=ROLE_ADMIN)

    def can_view(self, user):
        '''returns True if the user can display this printer'''
        return self.has_user(user)

    def can_modify(self, user):
        '''returns True if the user can modify this printer'''
        return self.is_admin(user)

    def set_user(self, user, role=None):
        '''Sets `user`'s access to the printer to `role`.

        If `role` is None, the user losts it's access to the printer.
        If `user` already has an access to the printer it will be overwritten.
        '''

        if role is None:
            UserOnPrinter.objects.filter(printer=self, user=user).delete()
        else:
            relationship, created = UserOnPrinter.objects.get_or_create(
                printer=self,
                user=user,
            )
            relationship.role = role
            relationship.save()
            return relationship


class UserOnPrinter(models.Model):
    '''
    N:N table between `User` and `Printer` with `role` attribute.
    '''
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    printer = models.ForeignKey(Printer, on_delete=models.CASCADE)
    role = models.CharField('User role', default=ROLE_USER, blank=False, null=False, max_length=20, choices=ROLES)

    class Meta:
        constraints = (
            models.UniqueConstraint(fields=('printer', 'user'), name='Uniq_user_on_printer'),
        )

    def can_view(self, user):
        '''user can always view his / her own relationship'''
        return self.user == user or self.can_modify(user)

    def can_modify(self, user):
        '''only printer admin can change user relationship'''
        return self.printer.can_modify(user)

    def can_delete(self, user):
        '''user can remove self from printer (leave it)'''
        return self.user == user or self.can_modify(user)


class PrinterInGroup(models.Model):
    '''
    N:N table between `Printer` and `groups.Group`.
    '''
    printer = models.ForeignKey(Printer, on_delete=models.CASCADE)
    group = models.ForeignKey('groups.Group', on_delete=models.CASCADE)

    class Meta:
        constraints = (
            models.UniqueConstraint(fields=('printer', 'group'), name='Uniq_printer_in_group'),
        )

    def can_view(self, user):
        '''only printer admin can change user relationship'''
        return self.group.can_view(user)

    def can_modify(self, user):
        '''user can remove self from printer (leave it)'''
        return self.group.can_modify(user)

    def can_delete(self, user):
        '''user can remove self from printer (leave it)'''
        return self.user == user or self.can_modify(user)

from itertools import chain
from django.db import models
from users.models import User
from karmen import ROLE_ADMIN, ROLE_USER, ROLES
from karmen.utils import gen_short_uid
from karmen.models import IdField


class Group(models.Model):
    '''
    Printers can be organized in groups for easyer management
    '''

    id = IdField()
    name = models.CharField('Name', max_length=255, help_text='User friendly name of the group.')
    users = models.ManyToManyField(User, related_name='printer_groups', through='UserInGroup')

    def can_view(self, user):
        return UserInGroup.objects.filter(group=self, user=user).exists()

    def can_modify(self, user):
        return UserInGroup.objects.filter(group=self, user=user, role=ROLE_ADMIN).exists()

    def set_user(self, user, role=None):
        if role is None:
            self.users.remove(user)
        else:
            relationship, created = UserInGroup.objects.get_or_create(
                user=user,
                group=self,
            )
            relationship.role = role
            relationship.save()


class UserInGroup(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    role = models.CharField('User role', default=ROLE_USER, blank=False, null=False, max_length=20, choices=ROLES)

    class Meta:
        constraints = (
            models.UniqueConstraint(fields=('user', 'group'), name='Uniq_user_in_group'),
        )

    def can_view(self, user):
        return user == self.user or self.group.can_view(user)

    def can_modify(self, user):
        return self.group.can_modify(user)

    def can_delete(self, user):
        # user can leave group
        return user == self.user or self.can_modify(user)



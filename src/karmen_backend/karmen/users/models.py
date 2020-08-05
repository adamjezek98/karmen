from django.contrib.auth.models import AbstractUser
from django.db import models
from karmen.models import IdField

class User(AbstractUser):
    '''
    Karmen user has special implementation yet. It is created to make it easier
    to migrate to custom user in future.
    '''

    id = IdField()

    def can_view(self, user):
        return user == self

    def can_modify(self):
        return False

from django.db import models

# pylint: max_line_length=120
from itertools import chain
from django.db import models
from users.models import User
from karmen.utils import gen_short_uid
from karmen.models import IdField


class File(models.Model):
    '''
    File uploaded to Karmen
    '''

    id = IdField()
    name = models.CharField('Name', blank=False, max_length=255, help_text="Printer will be presented by this name.")
    file = models.FileField()
    group = models.ForeignKey('groups.Group', related_name='files', blank=False, on_delete=models.CASCADE)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_on = models.DateTimeField(auto_now_add=True)

    def delete(self, *args, **kwargs):
        storage, path = self.file.storage, self.file.path
        super().delete(*args, **kwargs)
        storage.delete(path)

    def can_view(self, user):
        return self.group.can_view(user)

    def can_modify(self, user):
        return self.group.can_modify(user)


    @classmethod
    def for_user(cls, user):
        return cls.objects.filter(group__users=user)

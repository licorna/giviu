from django.db import models
from giviu.utils import get_now


class BetaRegisteredUser(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=80, blank=True)
    email = models.EmailField(max_length=254, unique=True)
    ip = models.CharField(max_length=15, blank=True)
    comment = models.TextField(max_length=500, blank=True)
    created = models.DateTimeField(default=lambda: get_now())

    class Meta:
        db_table = 'beta_registered_user'

from django.db import models
from giviu.models import Merchants


class ApiClientId(models.Model):
    id = models.AutoField(primary_key=True)
    client_id = models.CharField(max_length=56)
    merchant = models.ForeignKey(Merchants,
                                 db_column='merchant_id',
                                 related_name='+')

    class Meta:
        db_table = 'apiclientid'

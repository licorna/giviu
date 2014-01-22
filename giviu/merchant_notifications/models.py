from django.db import models
from merchant.models import Merchants


class MerchantNotification(models.Model):
    '''MerchatNotification refers to a HTTP notification (request) to
    send to a given merchant triggered by an action.'''
    id = models.AutoField(primary_key=True)
    merchant = models.ForeignKey(Merchants, db_column='merchant_id')
    name = models.CharField(max_length=40, blank=False)
    endpoint = models.CharField(max_length=255)
    http_method = models.CharField(max_length=6)
    post_params = models.CharField(max_length=255)

    class Meta:
        db_table = 'merchant_notification'

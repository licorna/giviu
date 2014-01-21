from django.dispatch import Signal
from django.dispatch import receiver
from models import MerchantNotification
from merchant.models import Merchants
import requests
import logging
logger = logging.getLogger(__name__)


merchant_notification = Signal()


@receiver(merchant_notification)
def handle_merchant_notification(sender, **kwargs):
    merchant = kwargs.get('merchant')
    merchant = Merchants.objects.get(id=merchant)
    notifications = MerchantNotification.objects.filter(merchant=merchant)
    for notification in notifications:
        post = get_dict_from_params(notification.post_params, kwargs)
        if notification.http_method == 'POST':
            try:
                response = requests.post(notification.endpoint, data=post)
            except requests.exceptions.RequestException:
                logger.error('Exception when sending request to merchant')
            print response.text
            if response.status_code > 299:
                logger.warning('Response from merchant was > 299')
            else:
                logger.info('Response from merchant was ok')


def get_dict_from_params(params, args):
    data = {}
    for param in params.split('&'):
        key, value = param.split('=')
        if value == '?':
            value = args[key]
        data[key] = value

    return data

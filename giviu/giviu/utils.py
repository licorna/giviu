from datetime import datetime, timedelta
from django.contrib import sitemaps
from django.core.urlresolvers import reverse
from django.conf import settings


class GiftcardsSitemap(sitemaps.Sitemap):
    priority = 0.6
    frequency = 'daily'
    protocol = 'http' if settings.DEBUG else 'https'

    def items(self):
        from models import Giftcard
        return Giftcard.objects.all()


class CategoriesSitemap(sitemaps.Sitemap):
    priority = 0.5
    frequency = 'weekly'
    protocol = 'http' if settings.DEBUG else 'https'

    def items(self):
        from models import GiftcardCategory
        return GiftcardCategory.objects.all()


class PartnersSitemap(sitemaps.Sitemap):
    priority = 0.4
    frequency = 'weekly'
    protocol = 'http' if settings.DEBUG else 'https'

    def items(self):
        from merchant.models import Merchants
        return Merchants.objects.all()


MYSQL_DATE_FORMAT = '%Y-%m-%d'
MYSQL_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'


def get_today():
    return datetime.now().strftime(MYSQL_DATE_FORMAT)


def get_one_month():
    return (datetime.now() + timedelta(days=31)).strftime(MYSQL_DATE_FORMAT)


def get_now():
    return datetime.now().strftime(MYSQL_DATETIME_FORMAT)

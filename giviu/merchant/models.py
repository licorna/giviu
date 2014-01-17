from django.db import models
from api.models import ApiClientId


class MerchantTabs(models.Model):
    id = models.IntegerField(primary_key=True)
    parent_id = models.IntegerField()
    title = models.CharField(max_length=255)
    content = models.TextField()

    class Meta:
        db_table = 'merchant_tabs'
        verbose_name_plural = 'Merchant Tabs'


class Merchants(models.Model):
    id = models.AutoField(primary_key=True)
    created = models.DateTimeField()
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    tags = models.CharField(max_length=255)
    contact_name = models.CharField(max_length=255)
    contact_email = models.CharField(max_length=255)
    contact_phone = models.CharField(max_length=255)
    contact_rut = models.CharField(max_length=255, blank=True)
    rut = models.CharField(max_length=255, blank=True)
    website = models.CharField(max_length=255, blank=True)
    plan = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    logo = models.CharField(max_length=255, blank=True)
    lat = models.CharField(max_length=255, blank=True)
    lng = models.CharField(max_length=255, blank=True)

    def get_api_client_id(self):
        try:
            # TODO: multiple objects returned
            client_id = ApiClientId.objects.get(merchant=self)
        except ApiClientId.DoesNotExist:
            return None
        return client_id

    def get_customers(self):
        from giviu.models import Product, Users
        products = Product.objects.filter(giftcard__merchant=self)
        customers = Users.objects.filter(pk__in=[p.giftcard_from.id for p in products])
        return customers

    def get_absolute_url(self):
        return '/partner/' + self.slug

    class Meta:
        db_table = 'merchants'
        verbose_name_plural = 'Merchants'

    def __unicode__(self):
        return self.name


class MerchantUsers(models.Model):
    id = models.IntegerField(primary_key=True)
    merchant = models.ForeignKey('Merchants')
    store = models.IntegerField()
    name = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    permission = models.IntegerField()

    class Meta:
        db_table = 'merchant_users'
        verbose_name_plural = 'Merchant Users'

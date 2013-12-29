# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines for those models you wish to give write DB access
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)
from uuid import uuid4
from utils import get_today, get_one_month

class Calendar(models.Model):
    id = models.IntegerField(primary_key=True)
    user = models.ForeignKey('Users')
    friend_fbid = models.CharField(max_length=255, blank=True)
    when = models.DateField(blank=True, null=True)
    title = models.CharField(max_length=255, blank=True)
    friend_gender = models.CharField(max_length=50, blank=True)
    class Meta:
        db_table = 'calendar'

class Provincia(models.Model):
    id = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=64)
    region = models.ForeignKey('Region')
    class Meta:
        db_table = 'provincia'

class Region(models.Model):
    id = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=64)
    ordinal = models.IntegerField()
    class Meta:
        db_table = 'region'

class Comuna(models.Model):
    id = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=64)
    provincia = models.ForeignKey('Provincia')
    class Meta:
        db_table = 'comuna'

class Customer(models.Model):
    id = models.IntegerField(primary_key=True)
    parent_id = models.IntegerField()
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    birthday = models.DateField(blank=True, null=True)
    phone = models.CharField(max_length=255)
    hash = models.CharField(max_length=255)
    created = models.DateTimeField()
    class Meta:
        db_table = 'customer'


class Discount(models.Model):
    id = models.IntegerField(primary_key=True)
    user = models.ForeignKey('Users')
    quantity = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=255)
    reason = models.TextField()
    class Meta:
        db_table = 'discount'


class GiftcardCategory(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    parent_id = models.IntegerField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def count(self):
        return Giftcard.objects.filter(category__exact=self).count()

    class Meta:
        db_table = 'giftcard_category'
        verbose_name_plural = 'Giftcard Categories'

    def __unicode__(self):
        return self.name

class GiftcardDesign(models.Model):
    id = models.AutoField(primary_key=True)
    category = models.ForeignKey(GiftcardCategory)
    image = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    class Meta:
        db_table = 'giftcard_design'
        verbose_name_plural = 'Giftcard Designs'

    def __unicode__(self):
        return self.image


class Giftcard(models.Model):
    id = models.AutoField(primary_key=True)
    merchant = models.ForeignKey('Merchants', db_column='merchant_id')
    created = models.DateField()
    publication_date = models.DateField()
    unpublish_date = models.DateField()
    title = models.CharField(max_length=255)
    kind = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey('GiftcardCategory', db_column='category_id')
    price = models.CharField(max_length=255)
    quantity = models.IntegerField()
    image = models.CharField(max_length=255)
    stores = models.TextField(blank=True)
    status = models.IntegerField()
    sold_quantity = models.IntegerField()
    gender = models.CharField(max_length=20, blank=True)
    comuna = models.CharField(max_length=5, blank=True)
    provincia = models.CharField(max_length=5, blank=True)
    region = models.CharField(max_length=5, blank=True)
    fine_print = models.TextField()

    def __unicode__(self):
        return self.title

    def get_price(self):
        if ',' in self.price:
            return self.price.split(',')
        return self.price

    class Meta:
        db_table = 'giftcard'

class Product(models.Model):
    id = models.IntegerField(primary_key=True)
    hash = models.CharField(max_length=255)
    uuid = models.CharField(max_length=40, default=lambda:str(uuid4()))
    #parent = models.IntegerField()
    send_date = models.DateField(blank=True)
    created = models.DateTimeField(default=lambda:get_today())
    # giftcard_to = models.ForeignKey('Users', db_column='to', related_name='+')
    giftcard_to_email = models.CharField(db_column='to_email', max_length=255)
    giftcard_to_name = models.CharField(db_column='to_name', max_length=40)
    giftcard_from = models.ForeignKey('Users', db_column='from', related_name='+')
    comment = models.TextField()
    status = models.CharField(max_length=255)
    expiration_date = models.DateField(default=lambda:get_one_month())
    validation_date = models.DateTimeField(blank=True, null=True)
    design = models.ForeignKey(GiftcardDesign, db_column='design')
    price = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    giftcard = models.ForeignKey(Giftcard, db_column='giftcard_id')

    state = models.CharField(max_length=40, default='preparing')

    class Meta:
        db_table = 'product'


class Service(models.Model):
    id = models.IntegerField(primary_key=True)
    assigned = models.CharField(max_length=11)
    token = models.CharField(max_length=255)
    expiration_date = models.DateField()
    class Meta:
        db_table = 'service'

class Friend(models.Model):
    id = models.IntegerField(primary_key=True)
    me_fbid = models.CharField(max_length=25)
    fbid = models.CharField(max_length=25)
    name = models.CharField(max_length=255)
    month = models.CharField(max_length=40)
    day = models.CharField(max_length=40)
    birthday = models.DateField()
    gender = models.CharField(max_length=100)
    class Meta:
        db_table = 'friend'

class GiviuUserManager(BaseUserManager):
    def create_user(self, fbid, password, birthday, **kwargs):
        if not fbid:
            raise ValueError('Users must have an email address')

        user = self.model(
            fbid=fbid,
            birthday=birthday,
        )

        user.set_password(password)

        if 'email' in kwargs:
            user.email = kwargs['email']
        if 'location' in kwargs:
            user.location = kwargs['location']
        if 'first_name' in kwargs:
            user.first_name = kwargs['first_name']
        if 'last_name' in kwargs:
            user.last_name = kwargs['last_name']
        if 'gender' in kwargs:
            user.gender = kwargs['gender']

        user.save(using=self._db)
        return user


    def create_superuser(self, fbid, password, birthday):
        user = self.create_user(fbid,
            password=password,
            birthday=birthday
        )
        user.is_admin = True
        user.set_password(password)
        user.save(using=self._db)
        return user

class Users(AbstractBaseUser):
    id = models.IntegerField(primary_key=True)
    first_name = models.CharField(max_length=80, blank=True)
    last_name = models.CharField(max_length=80, blank=True)
    email = models.CharField(unique=True, max_length=255, blank=True)
    birthday = models.DateField()
    gender = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=20, blank=True)
    region = models.CharField(max_length=255, blank=True)
    provincia = models.CharField(max_length=255, blank=True)
    comuna = models.CharField(max_length=255, blank=True)
    friends = models.TextField(blank=True)
    created = models.DateField(blank=True, null=True)
    avatar = models.CharField(max_length=255, blank=True)
    last_purchase = models.DateField(blank=True, null=True)
    hash = models.CharField(max_length=255, blank=True)
    fbid = models.CharField(unique=True, max_length=25, blank=True)
    is_active = models.IntegerField(blank=True, null=True)
    is_admin = models.IntegerField(blank=True, null=True)

    objects = GiviuUserManager()
    USERNAME_FIELD = 'fbid'
    REQUIRED_FIELDS = ['birthday']

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    # On Python 3: def __str__(self):
    def __unicode__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

    class Meta:
        db_table = 'users'
        verbose_name_plural = 'Users'


class Likes(models.Model):
    id = models.IntegerField(primary_key=True)
    source_id = models.IntegerField()
    user = models.ForeignKey('Users')
    user_fbid = models.CharField(max_length=255)
    source_type = models.IntegerField()
    created = models.DateTimeField()
    class Meta:
        db_table = 'likes'
        verbose_name_plural = 'Likes'

class MerchantTabs(models.Model):
    id = models.IntegerField(primary_key=True)
    parent_id = models.IntegerField()
    title = models.CharField(max_length=255)
    content = models.TextField()
    class Meta:
        db_table = 'merchant_tabs'
        verbose_name_plural = 'Merchant Tabs'


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
    class Meta:
        db_table = 'merchants'
        verbose_name_plural = 'Merchants'

    def __unicode__(self):
        return self.name

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
from utils import get_now, get_three_month
from merchant.models import Merchants
from hashlib import sha224
from social.models import Likes
from datetime import datetime
from hashlib import md5
from external_codes import get_external_codes_for_giftcard
import logging
logger = logging.getLogger('giviu')


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


class CustomerInfo(models.Model):
    id = models.IntegerField(primary_key=True)
    merchant = models.ForeignKey(Merchants, db_column='merchant_id', related_name='+')
    user = models.ForeignKey('Users', db_column='user_id', related_name='+')
    data = models.TextField(blank=True)
    created = models.DateTimeField()

    class Meta:
        db_table = 'customer_info'


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
    priority = models.IntegerField(blank=True)

    def count(self):
        return Giftcard.objects.filter(category__exact=self, status=1).count()

    def get_absolute_url(self):
        return '/giftcard/category/' + self.slug

    @staticmethod
    def get_categories():
        return GiftcardCategory.objects.filter(status=1).order_by('priority')

    class Meta:
        db_table = 'giftcard_category'
        verbose_name_plural = 'Giftcard Categories'

    def __unicode__(self):
        return self.name


class GiftcardDesign(models.Model):
    id = models.AutoField(primary_key=True)
    #category = models.ForeignKey(GiftcardCategory)
    image = models.CharField(max_length=255)
    status = models.CharField(max_length=255)

    class Meta:
        db_table = 'giftcard_design'
        verbose_name_plural = 'Giftcard Designs'

    def __unicode__(self):
        return self.image


class GiftcardMedia(models.Model):
    id = models.AutoField(primary_key=True)
    media_type = models.CharField(max_length=24, default='image/png')
    url = models.CharField(max_length=512)
    giftcard = models.ForeignKey('Giftcard', db_column='giftcard_id',
                                 related_name='media')

    def __unicode__(self):
        return self.url

    class Meta:
        db_table = 'giftcard_media'


class Giftcard(models.Model):
    id = models.AutoField(primary_key=True)
    merchant = models.ForeignKey(Merchants, db_column='merchant_id')
    created = models.DateField()
    publication_date = models.DateField()
    unpublish_date = models.DateField()
    title = models.CharField(max_length=255)
    slug = models.CharField(max_length=511, blank=False, null=False)
    kind = models.CharField(max_length=255)
    priority = models.IntegerField(default=10)
    description = models.TextField()
    category = models.ForeignKey('GiftcardCategory', db_column='category_id')
    price = models.CharField(max_length=255)
    quantity = models.IntegerField()
    image = models.CharField(max_length=255)
    stores = models.TextField(blank=True)
    status = models.IntegerField(blank=False, default=1)
    sold_quantity = models.IntegerField()
    gender = models.CharField(max_length=20, blank=True)
    external_codes = models.BooleanField(default=False)
    fine_print = models.TextField()
    auto_validate = models.BooleanField(default=False)
    validation_info = models.TextField()

    def __unicode__(self):
        return self.title

    def get_price(self):
        if ',' in self.price:
            return self.price.split(',')
        return self.price

    def get_likes_qty(self):
        response = Likes.get_giftcard_likes(self.id, just_count=True)
        return response

    def get_likes(self):
        return Likes.get_giftcard_likes(self.id, just_count=False)

    def get_absolute_url(self):
        return '/giftcard/detail/' + self.slug

    def get_validation_info(self):
        from markdown2 import markdown as md
        if self.validation_info is not None:
            return md(self.validation_info)
        return ''

    def media_images(self):
        return self.media.filter(media_type='image/png')

    def pretty_fine_print(self):
        if '<' in self.fine_print:
            return self.fine_print
        from markdown2 import markdown as md
        return md(self.fine_print)

    def get_external_code(self):
        external_code = get_external_codes_for_giftcard(self)
        if external_code is None:
            logger.critical('No external codes for giftcard')
        return external_code

    class Meta:
        db_table = 'giftcard'


class Campaign(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=40)
    slug = models.CharField(max_length=20)
    color = models.CharField(max_length=9)
    giftcards = models.ManyToManyField(Giftcard)

    class Meta:
        db_table = 'campaign'


class Product(models.Model):
    # Los estados finales deberian ser cambiados
    # por estados que tengan sentido para un producto
    # y no necesariamente para una transaccion
    ALLOWED_STATES = ['PREPARING',
                      'WAITING_CONFIRMATION_FROM_PP',
                      'RESPONSE_FROM_PP_SUCCESS',
                      'RESPONSE_FROM_PP_ERROR',
                      'USING_CREDITS',
                      'USING_CREDITS_SUCCESS',
                      'USING_CREDITS_ERROR']

    id = models.IntegerField(primary_key=True)
    hash = models.CharField(max_length=255)
    uuid = models.CharField(max_length=40, default=lambda: str(uuid4()))
    validation_code = models.CharField(max_length=8)
    external_code = models.CharField(max_length=24, blank=True)
    send_date = models.DateField(blank=True)
    already_sent = models.IntegerField(default=0)
    created = models.DateTimeField(default=lambda: get_now())
    giftcard_to = models.ForeignKey('Users', db_column='to', related_name='+')
    giftcard_from = models.ForeignKey('Users', db_column='from', related_name='+')
    comment = models.TextField()
    status = models.CharField(max_length=255)
    expiration_date = models.DateField(default=lambda: get_three_month())
    validation_date = models.DateTimeField(blank=True, null=True)
    design = models.ForeignKey(GiftcardDesign, db_column='design')
    price = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    giftcard = models.ForeignKey(Giftcard, db_column='giftcard_id')

    validated = models.IntegerField(default=0)

    transaction = models.ForeignKey('PaymentTransaction',
                                    db_column='transaction_id',
                                    related_name='+')

    state = models.CharField(max_length=40, default='PREPARING')

    def set_state(self, state):
        last_state = self.state
        if state in Product.ALLOWED_STATES:
            self.state = state
            self.save()
            return last_state
        return False

    def is_closed(self):
        return self.state[:8] == 'RESPONSE'

    def save(self, *args, **kwargs):
        self.validation_code = self.uuid[:8]
        super(Product, self).save(*args, **kwargs)

    def get_validation_date(self):
        if self.validation_date is None:
            return 'No ha sido validada'
        return self.validation_date

    def get_validation_code(self):
        if self.giftcard.external_codes:
            return self.external_code
        return self.validation_code

    @classmethod
    def new(*args, **kwargs):
        product = Product(**kwargs)
        if product.giftcard.external_codes:
            product.external_code = product.giftcard.get_external_code()
        product.save()
        return product

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
    def create_inactive_user(self, email, name):
        user = self.model(
            email=email,
            fbid=sha224(email).hexdigest(),
            first_name=name,
        )
        #user.set_password()
        user.is_active = 0
        user.is_receiving = 1
        user.save()
        return user

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
                                birthday=birthday)
        user.is_admin = True
        user.set_password(password)
        user.save(using=self._db)
        return user


class Users(AbstractBaseUser):
    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=80, blank=True)
    last_name = models.CharField(max_length=80, blank=True)
    email = models.CharField(unique=True, max_length=255, blank=True)
    phone = models.CharField(max_length=16, blank=True)
    birthday = models.CharField(max_length=12)
    gender = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=20, blank=True)
    region = models.CharField(max_length=255, blank=True)
    provincia = models.CharField(max_length=255, blank=True)
    comuna = models.CharField(max_length=255, blank=True)
    friends = models.TextField(blank=True)
    created = models.DateField(blank=True, null=True, default=lambda: datetime.now())
    avatar = models.CharField(max_length=255, blank=True)
    last_purchase = models.DateField(blank=True, null=True)
    hash = models.CharField(max_length=255, blank=True)
    referer = models.CharField(blank=False, max_length=8, default=lambda: str(uuid4())[:8])
    fbid = models.CharField(unique=True, max_length=56, blank=True)
    is_active = models.IntegerField(null=False, blank=False, default=1)
    is_admin = models.IntegerField(null=False, blank=False, default=0)
    is_receiving = models.IntegerField(null=False, blank=False, default=0)
    is_merchant = models.IntegerField(null=False, blank=False, default=0)
    merchant = models.ForeignKey(Merchants, blank=True, db_column='merchant_id')

    objects = GiviuUserManager()
    USERNAME_FIELD = 'fbid'
    REQUIRED_FIELDS = []

    def get_full_name(self):
        if self.first_name != '' and self.last_name != '':
            return self.first_name + ' ' + self.last_name
        if self.first_name != '' and self.last_name == '':
            return self.first_name
        return self.email

    def get_birthday(self):
        if self.birthday is None:
            return ''
        return self.birthday

    def is_normal_user(self):
        return (len(self.fbid) < 56 and self.is_merchant == 0)

    def get_short_name(self):
        return self.first_name

    def __unicode__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    def get_related_merchant(self):
        if self.is_merchant:
            return self.admin_of

    def get_user_image(self, size=40):
        result = ''
        try:
            fbid = int(self.fbid)
            result = 'https://graph.facebook.com/%d/picture?width=%d&height=%d' % (fbid, size, size)
        except ValueError:
            result = 'https://www.gravatar.com/avatar/' + md5(self.email).hexdigest() + '?d=mm&size=' + str(size)
        return result


    def get_user_image_big(self):
        return self.get_user_image(200)

    def get_friend_likes_for_giftcard(self, giftcard_id):
        likes = Likes.get_likes_from_friends(self.fbid, giftcard_id)
        return likes

    @property
    def is_staff(self):
        return self.is_admin

    class Meta:
        db_table = 'users'
        verbose_name_plural = 'Users'


class GiviuAuthenticationBackend(object):
    def authenticate(self, username=None, password=None):
        try:
            if '@' in username:
                user = Users.objects.get(email=username)
            else:
                user = Users.objects.get(fbid=username)
            if user.check_password(password):
                return user
        except Users.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return Users.objects.get(pk=user_id)
        except Users.DoesNotExist:
            return None


class PaymentTransaction(models.Model):
    ALLOWED_STATES = ['PREPARING',
                      'CREATED_IN_PP',
                      'CLIENT_BEING_SENT_TO_PP',
                      'NOTIFIED_BY_PP',
                      'INFO_REQUESTED_TO_PP',
                      'RESPONSE_FROM_PP_SUCCESS',
                      'RESPONSE_FROM_PP_ERROR',
                      'USING_CREDITS',
                      'USING_CREDITS_SUCCESS',
                      'USING_CREDITS_ERROR']

    id = models.AutoField(primary_key=True)
    transaction_uuid = models.CharField(max_length=40)
    origin_timestamp = models.CharField(max_length=60)
    auth_header = models.CharField(max_length=127)
    payment_method = models.CharField(max_length=40)
    operation_number = models.CharField(max_length=20)
    authorization_code = models.CharField(max_length=20)
    amount = models.CharField(max_length=10)
    use_credits = models.CharField(max_length=40, blank=True)
    state = models.CharField(max_length=30, default='PREPARING')
    psp_token = models.CharField(max_length=60)
    raw_response = models.TextField(blank=True)

    def set_state(self, state):
        last_state = self.state
        if state in PaymentTransaction.ALLOWED_STATES:
            self.state = state
            self.save()
            return last_state
        return False

    def is_closed(self):
        return self.state[:8] == 'RESPONSE'

    class Meta:
        db_table = 'payment_transaction'
        verbose_name_plural = 'Payment Transactions'

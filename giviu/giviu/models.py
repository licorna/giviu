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

class Calendar(models.Model):
    user_id = models.IntegerField(db_column='calendar-user-id') # Field renamed to remove unsuitable characters.
    user_fb_id = models.CharField(db_column='calendar-user-fb-id', max_length=25)
    friend_fb_id = models.CharField(db_column='calendar-friend-fb-id', max_length=255)
    month = models.CharField(db_column='calendar-month', max_length=2)
    day = models.CharField(db_column='calendar-day', max_length=2)
    title = models.CharField(db_column='calendar-title', max_length=255)
    friend_gender = models.CharField(db_column='calendar-friend-gender', max_length=50)
    class Meta:
        db_table = 'calendar'

class Comunas(models.Model):
    comuna_nombre = models.CharField(max_length=64)
    provincia_id = models.IntegerField()
    class Meta:
        db_table = 'comunas'

class Customers(models.Model):
    parent_id = models.IntegerField(db_column='customer-parent-id')
    creation_date = models.DateTimeField(db_column='customer-creation-date')
    name = models.CharField(db_column='customer-name', max_length=255)
    last_name = models.CharField(db_column='customer-last-name', max_length=255)
    email = models.CharField(db_column='customer-email', max_length=255)
    birthday = models.CharField(db_column='customer-birthday', max_length=255)
    phone = models.CharField(db_column='customer-phone', max_length=255)
    hash = models.CharField(db_column='customer-hash', max_length=255)
    class Meta:
        db_table = 'customers'

class Discount(models.Model):
    user_id = models.IntegerField(db_column='discount-user-id')
    quantity = models.IntegerField(db_column='discount-quantity')
    start_date = models.DateField(db_column='discount-start-date')
    end_date = models.DateField(db_column='discount-end-date')
    status = models.CharField(db_column='discount-status', max_length=255)
    reason = models.TextField(db_column='discount-reason')
    class Meta:
        db_table = 'discount'

class GiftcardCategory(models.Model):
    giftcardcategory_id = models.IntegerField(db_column='category-id', primary_key=True)
    name = models.CharField(db_column='category-name', max_length=255)
    slug = models.CharField(db_column='category-slug', max_length=255)
    status = models.CharField(db_column='category-status', max_length=255)
    parent_id = models.IntegerField(db_column='category-parent-id')
    description = models.TextField(db_column='category-description')
    class Meta:
        db_table = 'giftcard-category'

class GiftcardStyle(models.Model):
    category_id = models.IntegerField(db_column='giftcard-style-category-id')
    image = models.CharField(db_column='giftcard-style-image', max_length=255)
    status = models.CharField(db_column='giftcard-style-status', max_length=255)
    class Meta:
        db_table = 'giftcard-style'

class Giftcards(models.Model):
    _hash = models.CharField(db_column='giftcard-hash', max_length=255)
    parent = models.IntegerField(db_column='giftcard-parent')
    send_date = models.DateField(db_column='giftcard-send-date')
    creation_date = models.DateTimeField(db_column='giftcard-creation-date')
    to = models.CharField(db_column='giftcard-to', max_length=255)
    to_mail = models.CharField(db_column='giftcard-to-mail', max_length=255)
    comment = models.TextField(db_column='giftcard-comment')
    status = models.CharField(db_column='giftcard-status', max_length=255)
    id_sender = models.IntegerField(db_column='giftcard-id-sender')
    expiration_date = models.DateField(db_column='giftcard-expiration-date')
    validation_date = models.DateTimeField(db_column='giftcard-validation-date')
    style = models.CharField(db_column='giftcard-style', max_length=255)
    price = models.CharField(db_column='giftcard-price', max_length=255)
    _type = models.CharField(db_column='giftcard-type', max_length=255)
    product_id = models.CharField(db_column='giftcard-product-id', max_length=255)
    class Meta:
        db_table = 'giftcards'

class Likes(models.Model):
    likes_id = models.IntegerField(db_column='like-id', primary_key=True)
    source_id = models.IntegerField(db_column='like-source-id')
    user_id = models.IntegerField(db_column='like-user-id')
    user_fb_id = models.CharField(db_column='like-user-fb-id', max_length=255)
    source_type = models.IntegerField(db_column='like-source-type')
    creation_date = models.DateTimeField(db_column='like-creation-date')
    class Meta:
        db_table = 'likes'

class MerchantTabs(models.Model):
    parent_id = models.IntegerField(db_column='merchant-tabs-parent-id')
    title = models.CharField(db_column='merchant-tabs-title', max_length=255)
    content = models.TextField(db_column='merchant-tabs-content')
    class Meta:
        db_table = 'merchant-tabs'

class MerchantUsers(models.Model):
    parent_id = models.ForeignKey('Merchants', db_column='merchant-users-parent-id')
    store = models.IntegerField(db_column='merchant-users-store')
    name = models.CharField(db_column='merchant-users-name', max_length=255)
    username = models.CharField(db_column='merchant-users-username', max_length=255)
    email = models.CharField(db_column='merchant-users-email', max_length=255)
    phone = models.CharField(db_column='merchant-users-phone', max_length=255)
    password = models.CharField(db_column='merchant-users-password', max_length=255)
    permission = models.IntegerField(db_column='merchant-users-permission')
    class Meta:
        db_table = 'merchant-users'

class Merchants(models.Model):
    merchant_id = models.IntegerField(db_column='merchant-id', primary_key=True)
    creation_date = models.DateTimeField(db_column='merchant-creation-date')
    name = models.CharField(db_column='merchant-name', max_length=255)
    slug = models.CharField(db_column='merchant-slug', max_length=255)
    address = models.CharField(db_column='merchant-address', max_length=255)
    country = models.CharField(db_column='merchant-country', max_length=255)
    category = models.CharField(db_column='merchant-category', max_length=255)
    tags = models.CharField(db_column='merchant-tags', max_length=255)
    contact_name = models.CharField(db_column='merchant-contact-name', max_length=255)
    contact_email = models.CharField(db_column='merchant-contact-email', max_length=255)
    contact_phone = models.CharField(db_column='merchant-contact-phone', max_length=255)
    contact_rut = models.CharField(db_column='merchant-contact-rut', max_length=255)
    rut = models.CharField(db_column='merchant-rut', max_length=255)
    website = models.CharField(db_column='merchant-website', max_length=255)
    plan = models.CharField(db_column='merchant-plan', max_length=255)
    description = models.TextField(db_column='merchant-description')
    logo = models.CharField(db_column='merchant-logo', max_length=255)
    lat = models.CharField(db_column='merchant-lat', max_length=255)
    lon = models.CharField(db_column='merchant-long', max_length=255)
    class Meta:
        db_table = 'merchants'

class Products(models.Model):
    product_id = models.IntegerField(db_column='product-id', primary_key=True)
    merchant_id = models.CharField(db_column='product-merchant-id', max_length=255)
    creation_date = models.DateField(db_column='product-creation-date')
    publication_date = models.DateField(db_column='product-publication-date')
    unpublish_date = models.DateField(db_column='product-unpublish-date')
    title = models.CharField(db_column='product-title', max_length=255)
    type_ = models.CharField(db_column='product-type', max_length=255)
    description = models.TextField(db_column='product-description')
    category = models.CharField(db_column='product-category', max_length=255)
    price = models.CharField(db_column='product-price', max_length=255)
    quantity = models.CharField(db_column='product-quantity', max_length=255)
    image = models.CharField(db_column='product-image', max_length=255)
    stores = models.TextField(db_column='product-stores')
    status = models.IntegerField(db_column='product-status')
    sold_quantity = models.IntegerField(db_column='product-sold-quantity')
    gender = models.CharField(db_column='product-gender', max_length=10)
    comuna = models.CharField(db_column='product-comuna', max_length=5)
    provincia = models.CharField(db_column='product-provincia', max_length=5)
    region = models.CharField(db_column='product-region', max_length=5)
    fine_print = models.TextField(db_column='product-fine-print')
    class Meta:
        db_table = 'products'

    def __unicode__(self):
        return str(self.product_id) + ': ' + self.title

class Provincias(models.Model):
    nombre = models.CharField(max_length=64)
    region_id = models.IntegerField()
    class Meta:
        db_table = 'provincias'

class Regiones(models.Model):
    nombre = models.CharField(max_length=64)
    ordinal = models.CharField(max_length=4)
    class Meta:
        db_table = 'regiones'

class Services(models.Model):
    assigned = models.CharField(db_column='service-assigned', max_length=11)
    token = models.CharField(db_column='service-token', max_length=255)
    expiration_date = models.DateField(db_column='service-expiration-date')
    class Meta:
        db_table = 'services'

class UserFriends(models.Model):
    user_friends_id = models.IntegerField(db_column='user-friends-id', primary_key=True)
    me_fb_id = models.CharField(db_column='user-friend-me-fb-id', max_length=25)
    fb_id = models.CharField(db_column='user-friend-fb-id', max_length=25)
    name = models.CharField(db_column='user-friend-name', max_length=255)
    month = models.CharField(db_column='user-friend-month', max_length=40)
    day = models.CharField(db_column='user-friend-day', max_length=40)
    birthday = models.CharField(db_column='user-friend-birthday', max_length=25)
    gender = models.CharField(db_column='user-friend-gender', max_length=100)
    class Meta:
        db_table = 'user-friends'

class Users(models.Model):
    name = models.CharField(db_column='user-name', max_length=255)
    last_name = models.CharField(db_column='user-last-name', max_length=255)
    email = models.CharField(db_column='user-email', max_length=255)
    birthday = models.CharField(db_column='user-birthday', max_length=255)
    gender = models.CharField(db_column='user-gender', max_length=255)
    country = models.CharField(db_column='user-country', max_length=255)
    region = models.CharField(db_column='user-region', max_length=255)
    provincia = models.CharField(db_column='user-provincia', max_length=255)
    comuna = models.CharField(db_column='user-comuna', max_length=255)
    password = models.CharField(db_column='user-password', max_length=255)
    friends = models.TextField(db_column='user-friends')
    creation_date = models.DateField(db_column='user-creation-date')
    last_log_off = models.DateField(db_column='user-last-log-off')
    avatar = models.CharField(db_column='user-avatar', max_length=255)
    favorite_category = models.IntegerField(db_column='user-favorite-category')
    last_purchase = models.DateField(db_column='user-last-purchase')
    _hash = models.CharField(db_column='user-hash', max_length=255)
    fb_id = models.CharField(db_column='user-fb-id', max_length=25)
    class Meta:
        db_table = 'users'

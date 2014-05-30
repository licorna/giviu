from django.http import HttpResponseBadRequest
from django.shortcuts import (render_to_response, redirect,
                              get_object_or_404)
from django.core.context_processors import csrf
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import AnonymousUser
from django.db.models import Q
from django.db import transaction as db_transaction
from django.template import RequestContext
from django.contrib.auth.decorators import login_required, user_passes_test
from models import (
    GiftcardCategory, Giftcard, GiftcardDesign, Campaign,
    Users, Product, ProductDeliveryInformation
)
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from merchant.models import MerchantTabs, Merchants
from social.models import Likes
from marketing import event_user_registered
from credits import (user_credits, use_user_credits, add_user_credits,
                     add_user_referer)
from utils import get_data_for_header, calculate_delivery_price

from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.views.decorators.http import require_POST
from django.conf import settings

from datetime import datetime, timedelta

import logging
logger = logging.getLogger('giviu')


def user_is_normal_user(user):
    return isinstance(user, AnonymousUser) or (
        isinstance(user, Users) and user.is_normal_user())


def do_logout(request):
    logout(request)
    return redirect('/')


def do_register(request):
    if request.user.is_authenticated():
        return redirect('home')

    if request.method == 'POST':
        required_parameters = frozenset(('facebookId', 'email', 'location',
                                         'name', 'lastName', 'gender',
                                         'birth'))

        if required_parameters <= frozenset(request.POST):

            facebook_id = request.POST['facebookId']
            email = request.POST['email']
            location = request.POST['location']
            first_name = request.POST['name']
            last_name = request.POST['lastName']
            gender = request.POST['gender']
            birthday = request.POST['birth']
            #birthday = birthday[6:] + '-' + birthday[0:2] + '-' + birthday[3:5]
            referer = request.POST.get('referer', None)
            full_name = first_name + ' ' + last_name

            try:
                # If user does not exists, check for a user with
                # same email.
                user = Users.objects.get(email=email)
                user.fbid = facebook_id
                user.birthday = birthday
                user.first_name = first_name
                user.last_name = last_name
                user.gender = gender
                user.location = location
                user.is_receiving = 0
                user.is_active = 1
                user.save()

            except Users.DoesNotExist:
                # If there is no user with this facebook_id and no
                # user with this email, then it is a completely new user
                user = Users.objects.create_user(facebook_id, facebook_id,
                                                 birthday,
                                                 email=email,
                                                 location=location,
                                                 first_name=first_name,
                                                 last_name=last_name,
                                                 gender=gender)
            # Send email to registered user.!
            event_user_registered(user.email, user.get_full_name())
            add_user_credits(facebook_id, 2000, 'Giviu Registration Credits')
            if referer is not None:
                try:
                    user = Users.objects.get(referer=referer)
                except Users.DoesNotExist:
                    logger.info('Unable to find %s referer.' % (referer))
                add_user_referer(user.fbid, facebook_id)
        else:
            if 'facebookId' in request.POST:
                facebook_id = request.POST['facebookId']
                try:
                    user = Users.objects.get(fbid=facebook_id)
                except Users.DoesNotExist:
                    return HttpResponseBadRequest()
            else:
                return HttpResponseBadRequest()

        if user and user.is_active == 1 and not user.is_merchant:
            user = authenticate(username=facebook_id, password=facebook_id)
            if not user:
                return HttpResponseBadRequest()

            login(request, user)
            return redirect('/')
        else:
            print 'LOG: No se pudo crear el usuario'

    c = {}
    c.update(csrf(request))
    return render_to_response('register.html', c,
                              context_instance=RequestContext(request))


def home(request, slug=None, division=None):
    data = {}
    show_title = False

    search = request.GET.get('q', None)
    if not division:
        if search and len(search) > 2:
            data.update({'search': True, 'search_term': search})
            products = Giftcard.objects.filter(Q(status=1),
                                    Q(title__contains=search) |
                                    Q(description__contains=search))
        else:
            products = Giftcard.objects.filter(status=1).order_by('-priority')

    if division == 'category':
        products = cache.get('products/category/' + slug)
        category = cache.get('category/' + slug)
        if not products or not category:
            category = get_object_or_404(GiftcardCategory, slug=slug)
            products = Giftcard.objects.filter(category=category.id,
                                               status=1).order_by('-priority')
            cache.set('products/category/' + slug, products)
            cache.set('category/' + slug, category)
        else:
            print products
        show_title = True
        data.update({'this_category': category})

    if division == 'campaign':
        products = cache.get('products/campaign/' + slug)
        campaign = cache.get('campaign/' + slug)
        if not products or not campaign:
            campaign = get_object_or_404(Campaign, slug=slug)
            products = campaign.giftcards.filter(status=1).order_by('-priority')
            cache.set('products/campaign/' + slug, products)
            cache.set('campaign/' + slug, campaign)
        data.update({'this_campaign': campaign})

    if request.user.is_authenticated() and settings.SOCIAL['FETCH_FRIEND_LIKES']:
        for product in products:
            product.get_friend_likes = Likes.get_likes_from_friends(request.user.fbid,
                                                                    product.id)
            product.get_own_like = Likes.does_user_likes(request.user.fbid,
                                                         product.id)

    campaigns = cache.get('campaigns/')
    if not campaigns:
        campaigns = Campaign.objects.order_by('id')
        cache.set('campaigns/', campaigns)

    data.update({
        'products': products,
        #'all_products_len': all_product_len,
        'show_title': show_title,
        'campaigns' : campaigns,
    })
    data.update(get_data_for_header(request))
    if slug:
        data.update({'slug': slug})
    return render_to_response('giftcard.html', data,
                              context_instance=RequestContext(request))


@user_passes_test(user_is_normal_user, login_url='/logout')
def giftcard_detail(request, slug):
    giftcard = get_object_or_404(Giftcard, slug=slug)
    likes = Likes.get_giftcard_likes(giftcard.id)
    if request.user.is_authenticated():
        user_like = Likes.does_user_likes(request.user.fbid, giftcard.id)
    else:
        user_like = 0
    friends = []
    data = {
        'giftcard': giftcard,
        'likes': likes,
        'friends': friends,
        'user_like': user_like
    }
    data.update(get_data_for_header(request))
    return render_to_response('giftcard_details.html', data,
                              context_instance=RequestContext(request))


@user_passes_test(user_is_normal_user, login_url='/logout')
@login_required
def giftcard_custom(request, slug):
    giftcard = get_object_or_404(Giftcard, slug=slug)
    if giftcard.is_product:
        data = dict(giftcard=giftcard)
        return render_to_response('product_delivery_custom.html', data,
                                  context_instance=RequestContext(request))
    style = GiftcardDesign.objects.filter(status='publish')
    data = {
        'giftcard': giftcard,
        'styles': style,
    }
    data.update(get_data_for_header(request))
    return render_to_response('giftcard_custom.html', data,
                              context_instance=RequestContext(request))


@login_required
@user_passes_test(user_is_normal_user, login_url='/logout')
def user(request):
    products = Product.objects.filter(giftcard_to=request.user,
                                      state='RESPONSE_FROM_PP_SUCCESS',
                                      already_sent=1)
    data = {
        'products': products,
    }
    data.update(get_data_for_header(request))
    return render_to_response('user.html',
                              data,
                              context_instance=RequestContext(request))


@login_required
@user_passes_test(user_is_normal_user, login_url='/logout')
def sent(request):
    products = Product.objects.filter(giftcard_from=request.user,
                                      state='RESPONSE_FROM_PP_SUCCESS')
    data = {
        'products': products,
    }
    data.update(get_data_for_header(request))
    return render_to_response('user_sent.html',
                              data,
                              context_instance=RequestContext(request))


@login_required
@user_passes_test(user_is_normal_user, login_url='/logout')
def calendar(request):
    data = {}
    data.update(get_data_for_header(request))
    return render_to_response('user_calendar.html',
                              data,
                              context_instance=RequestContext(request))


@require_POST
@login_required
@user_passes_test(user_is_normal_user, login_url='/logout')
def giftcard_confirmation(request):
    from puntopagos import transaction_create
    from credits import transaction_create_no_psp

    for datum in ['giftcard-id', 'product-merchant-id']:
        if datum not in request.POST:
            return HttpResponseBadRequest()


    giftcard = Giftcard.objects.get(pk=request.POST.get('giftcard-id'))

    if 'email-to' not in request.POST and 'auto-validate' not in request.POST and\
       not giftcard.is_product:
        return HttpResponseBadRequest()

    ribbon = ''
    paper = ''
    delivery_information = ''

    if giftcard.is_product:
        '''Fetch necessary information to create the product with delivery
        information.
        '''
        name_to = request.POST['name-to']
        email_to = 'auto_validate@giviu.com'
        comment = request.POST['comment']
        price = request.POST['giftcard-price']
        delivery_price = request.POST.get('delivery-price', 0)
        date = request.POST['send-when']
        address1 = request.POST['address_1']
        address2 = request.POST['address_2']
        address3 = request.POST['comunas']
        address_complete = request.POST['address']
        design = request.POST.get('giftcard-design', 1)
        ribbon = request.POST.get('ribbon-color', 0)
        paper = request.POST.get('paper-color', 0)
        validated = 1
        already_sent = 0
        trx_credit = user_credits(request.user.fbid)
        try:
            price = int(price)
            delivery_price = int(delivery_price)
        except ValueError:
            return HttpResponseBadRequest()

        credits = {'uuid': 'none'}
        credits_used = 0
        original_price = price
        if trx_credit['amount'] > 0:
            if trx_credit['amount'] >= price:
                credits_used = price
                price = 0
            else:
                credits_used = trx_credit['amount']
                price = price - credits_used
                credits = use_user_credits(request.user.fbid, credits_used)
    elif 'auto-validate' not in request.POST:
        email_to = request.POST['email-to']
        name_to = request.POST['name-to']
        comment = request.POST['comment']
        price = request.POST['giftcard-price']
        design = request.POST.get('giftcard-design', None)
        date = request.POST['send-when']
        validated = 0
        already_sent = 0
        try:
            validate_email(email_to)
        except ValidationError:
            return HttpResponseBadRequest()

        trx_credit = user_credits(request.user.fbid)
        try:
            price = int(price)
        except ValueError:
            return HttpResponseBadRequest()

        credits = {'uuid': 'none'}
        credits_used = 0
        original_price = price
        if trx_credit['amount'] > 0:
            if trx_credit['amount'] >= price:
                credits_used = price
                price = 0
            else:
                credits_used = trx_credit['amount']
                price = price - credits_used
            credits = use_user_credits(request.user.fbid, credits_used)

    else:
        validated = 1
        already_sent = 1
        email_to = 'auto_validate@giviu.com'
        date = datetime.today()
        name_to = 'Auto Validate'
        price = request.POST.get('giftcard-price', None)
        try:
            price = int(price)
        except ValueError:
            return HttpResponseBadRequest()
        design = request.POST.get('giftcard-design', 1)
        comment = request.POST.get('comment', '')
        original_price = price

    try:
        giftcard = Giftcard.objects.get(pk=int(request.POST['giftcard-id']))
    except Giftcard.DoesNotExist:
        return HttpResponseBadRequest()

    design = GiftcardDesign.objects.get(pk=int(design))

    checkout_price = price
    if giftcard.is_product:
        checkout_price += delivery_price

    if checkout_price > 0:
        #TODO: Comprobar que la transaccion fue creada exitosamente
        response, transaction = transaction_create(str(checkout_price))
        try:
            trx_id = response['trx_id']
        except KeyError:
            logger.critical('Transaction was not created')
    else:
        response, transaction = transaction_create_no_psp(str(checkout_price))
        trx_id = response['trx_id']

    if 'auto-validate' not in request.POST:
        if credits['uuid'] is not 'none':
            transaction.use_credits = credits['uuid']
            transaction.save()
        else:
            transaction.use_credits = None
    else:
        credits_used = 0

    try:
        customer = Users.objects.get(email=email_to)
    except Users.DoesNotExist:
        customer = Users.objects.create_inactive_user(email_to, name_to)
        customer = Users.objects.get(email=email_to)

    if isinstance(date, basestring):
        date = datetime.strptime(date, '%Y-%m-%d')

    product = Product.new(giftcard_from=request.user,
                          giftcard_to=customer,
                          price=price + credits_used + delivery_price,
                          design=design,
                          send_date=date,
                          expiration_date=date + timedelta(days=90),
                          comment=comment,
                          giftcard=giftcard,
                          transaction=transaction,
                          validated=validated,
                          already_sent=already_sent)

    # TODO: why is this?
    product = Product.objects.get(uuid=product.uuid)

    if giftcard.is_product:
        delivery_information = ProductDeliveryInformation(
            product=product,
            address=' '.join([address1, address2, address3]),
            ribbon_color=ribbon,
            package_color=paper
        )
        delivery_information.save()
    product_id = product.uuid

    data = {
        'name_to': name_to,
        'email_to': email_to,
        'send_date': date,
        'comment': comment,
        'price': price,
        'original_price': original_price,
        'giftcard_design': design.id,
        'giftcard': giftcard,
        'giftcard_image': giftcard.image,
        'product_id': product_id,
        'token': response['token'],
        'trx_id': trx_id,
        'design': product.design,
        'ribbon': ribbon,
        'paper': paper,
        'delivery_address': delivery_information.address,
        'delivery_price': delivery_price,
    }
    data.update(csrf(request))
    return render_to_response('checkout_confirmation.html',
                              data,
                              context_instance=RequestContext(request))


@user_passes_test(user_is_normal_user, login_url='/logout')
def product_show(request, uuid):
    product = get_object_or_404(Product, uuid=uuid)
    data = {
        'product': product,
        'hash': product.validation_code,
    }

    data.update(get_data_for_header(request))
    return render_to_response('product_show.html', data,
                              context_instance=RequestContext(request))


@user_passes_test(user_is_normal_user, login_url='/logout')
def partner_info(request, merchant_slug):
    merchant = get_object_or_404(Merchants, slug=merchant_slug)
    tabs = MerchantTabs.objects.filter(parent_id=merchant.id)
    products = Giftcard.objects.filter(merchant=merchant.id, status=1)
    if request.user.is_authenticated() and settings.SOCIAL['FETCH_FRIEND_LIKES']:
        for product in products:
            product.get_friend_likes = Likes.get_likes_from_friends(request.user.fbid,
                                                                    product.id)
            product.get_own_like = Likes.does_user_likes(request.user.fbid,
                                                         product.id)

    data = {
        'merchant': merchant,
        'products': products,
        'tabs': tabs,
    }

    data.update(get_data_for_header(request))
    return render_to_response('partner_info.html', data,
                              context_instance=RequestContext(request))


def response_not_found(request):
    data = {}

    data.update(get_data_for_header(request))
    return render_to_response('404.html', data,
                              context_instance=RequestContext(request))


def search(request):
    data = {}
    data.update(get_data_for_header(request))
    return render_to_response('search.html', data,
                              context_instance=RequestContext(request))


def page_who_we_are(request):
    data = {}
    data.update(get_data_for_header(request))
    return render_to_response('page_who_we_are.html', data,
                              context_instance=RequestContext(request))


def page_who_its_work(request):
    data = {}
    data.update(get_data_for_header(request))
    return render_to_response('page_who_its_work.html', data,
                              context_instance=RequestContext(request))


def page_faq(request):
    data = {}
    data.update(get_data_for_header(request))
    return render_to_response('page_faq.html', data,
                              context_instance=RequestContext(request))


def page_enterprise(request):
    data = {}
    data.update(get_data_for_header(request))
    return render_to_response('page_enterprise.html', data,
                              context_instance=RequestContext(request))

def page_contact(request):
    data = {}
    data.update(get_data_for_header(request))
    return render_to_response('page_contact.html', data,
                              context_instance=RequestContext(request))

def interviews(request):
    data = {}
    data.update(get_data_for_header(request))
    return render_to_response('interviews.html', data,
                              context_instance=RequestContext(request))

def page_terms(request):
    data = {}
    data.update(get_data_for_header(request))
    return render_to_response('page_terms.html', data,
                              context_instance=RequestContext(request))

def new_custom_gift(request):
    data = {}
    data.update(get_data_for_header(request))
    return render_to_response('new_custom_gift.html', data,
                              context_instance=RequestContext(request))

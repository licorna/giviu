from django.http import HttpResponseBadRequest
from django.shortcuts import (render_to_response, redirect,
                              get_object_or_404)
from django.core.context_processors import csrf
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import AnonymousUser
from django.template import RequestContext
from django.contrib.auth.decorators import login_required, user_passes_test
from models import (
    GiftcardCategory, Giftcard, GiftcardDesign,
    Users, Product
)
from merchant.models import MerchantTabs, Merchants
from social.models import Likes
from marketing import event_user_registered

from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.views.decorators.http import require_POST

import logging
logger = logging.getLogger(__name__)


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
                user.is_receiving = 0
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
            # Send email to registered user.!
            event_user_registered(user.email, user.get_full_name())

            login(request, user)
            return redirect('/')
        else:
            print 'LOG: No se pudo crear el usuario'

    c = {}
    c.update(csrf(request))
    return render_to_response('register.html', c,
                              context_instance=RequestContext(request))


def home(request, slug=None):
    categories = GiftcardCategory.objects.all()
    data = {}
    if slug:
        category = GiftcardCategory.objects.get(slug__exact=slug)
        products = Giftcard.objects.filter(category__exact=category.id,
                                           status=1)
        show_title = True
        data = {
            'this_category': category,
        }
    else:
        show_title = False
        products = Giftcard.objects.filter(status=1)
    all_product_len = Giftcard.objects.filter(status=1).count()

    if request.user.is_authenticated():
        for product in products:
            product.get_friend_likes = Likes.get_likes_from_friends(request.user.fbid, product.id)
            product.get_own_like = Likes.does_user_likes(request.user.fbid,
                                                         product.id)

    data.update({
        'categories': categories,
        'products': products,
        'all_products_len': all_product_len,
        'show_title': show_title
    })
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
    return render_to_response('giftcard_details.html', data,
                              context_instance=RequestContext(request))


@user_passes_test(user_is_normal_user, login_url='/logout')
def giftcard_custom(request, slug):
    giftcard = get_object_or_404(Giftcard, slug=slug)
    style = GiftcardDesign.objects.filter(status='publish')
    data = {
        'giftcard': giftcard,
        'styles': style,
    }

    return render_to_response('giftcard_custom.html', data,
                              context_instance=RequestContext(request))


@login_required
@user_passes_test(user_is_normal_user, login_url='/logout')
def user(request):
    products = Product.objects.filter(giftcard_to=request.user, state='RESPONSE_FROM_PP_SUCCESS')
    data = {
        'products': products,
    }
    return render_to_response('user.html',
                              data,
                              context_instance=RequestContext(request))


@login_required
@user_passes_test(user_is_normal_user, login_url='/logout')
def sent(request):
    products = Product.objects.filter(giftcard_from=request.user, state='RESPONSE_FROM_PP_SUCCESS')
    data = {
        'products': products,
    }
    return render_to_response('user_sent.html',
                              data,
                              context_instance=RequestContext(request))


@login_required
@user_passes_test(user_is_normal_user, login_url='/logout')
def calendar(request):
    data = {}
    return render_to_response('user_calendar.html',
                              data,
                              context_instance=RequestContext(request))


@require_POST
@login_required
@user_passes_test(user_is_normal_user, login_url='/logout')
def giftcard_confirmation(request):
    from puntopagos import transaction_create

    for datum in ['giftcard-id', 'product-merchant-id', 'email-to']:
        if datum not in request.POST:
            return HttpResponseBadRequest()
    email_to = request.POST['email-to']
    name_to = request.POST['name-to']
    comment = request.POST['comment']
    price = request.POST['giftcard-price']
    design = request.POST['giftcard-design']
    date = request.POST['send-when']
    try:
        validate_email(email_to)
    except ValidationError:
        return HttpResponseBadRequest()

    try:
        giftcard = Giftcard.objects.get(pk=int(request.POST['giftcard-id']))
    except Giftcard.DoesNotExist:
        return HttpResponseBadRequest()

    design = GiftcardDesign.objects.get(pk=int(design))

    #TODO: Comprobar que la transaccion fue creada exitosamente
    response, transaction = transaction_create(price)
    try:
        trx_id = response['trx_id']
    except KeyError:
        #TODO: patalear
        pass

    try:
        customer = Users.objects.get(email=email_to)
    except Users.DoesNotExist:
        customer = Users.objects.create_inactive_user(email_to, name_to)
        customer = Users.objects.get(email=email_to)

    product = Product(giftcard_from=request.user,
                      giftcard_to=customer,
                      price=price,
                      design=design,
                      send_date=date,
                      comment=comment,
                      giftcard=giftcard,
                      transaction=transaction)
    product.save()
    product_id = product.uuid

    data = {
        'name_to': name_to,
        'email_to': email_to,
        'send_date': date,
        'comment': comment,
        'price': price,
        'giftcard_design': request.POST['giftcard-design'],
        'giftcard': giftcard,
        'product_id': product_id,
        'token': response['token'],
        'trx_id': trx_id,
        'design': product.design
    }
    data.update(csrf(request))

    return render_to_response('checkout_confirmation.html',
                              data,
                              context_instance=RequestContext(request))


@user_passes_test(user_is_normal_user, login_url='/logout')
def product_show(request, uuid):
    product = Product.objects.get(uuid__exact=uuid)
    data = {
        'product': product,
        'hash': product.validation_code

    }

    return render_to_response('product_show.html', data,
                              context_instance=RequestContext(request))


@user_passes_test(user_is_normal_user, login_url='/logout')
def partner_info(request, merchant_slug):
    merchant = get_object_or_404(Merchants, slug=merchant_slug)
    tabs = MerchantTabs.objects.filter(parent_id=merchant.id)
    products = Giftcard.objects.filter(merchant=merchant.id, status=1)
    if request.user.is_authenticated():
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

    return render_to_response('partner_info.html', data,
                              context_instance=RequestContext(request))


def response_not_found(request):
    data = ""
    return render_to_response('404.html',data,
                              context_instance=RequestContext(request))


def search(request):
    data = ""
    return render_to_response('search.html',data,
                              context_instance=RequestContext(request))


def page_who_we_are(request):
    data = ""
    return render_to_response('page_who_we_are.html',data,
                              context_instance=RequestContext(request))


def page_who_its_work(request):
    data = ""
    return render_to_response('page_who_its_work.html',data,
                              context_instance=RequestContext(request))


def page_faq(request):
    data = ""
    return render_to_response('page_faq.html',data,
                              context_instance=RequestContext(request))


def page_enterprise(request):
    data = ""
    return render_to_response('page_enterprise.html',data,
                              context_instance=RequestContext(request))


def page_contact(request):
    data = ""
    return render_to_response('page_contact.html',data,
                              context_instance=RequestContext(request))


def page_terms(request):
    data = ""
    return render_to_response('page_terms.html',data,
                              context_instance=RequestContext(request))

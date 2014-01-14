from django.http import HttpResponseBadRequest
from django.shortcuts import render_to_response, redirect
from django.core.context_processors import csrf
from django.contrib.auth import authenticate, login, logout
from django.template import RequestContext
from django.contrib.auth.decorators import login_required, user_passes_test
from models import (
    GiftcardCategory, Giftcard, GiftcardDesign,
    Users, Product
)
from merchant.models import MerchantTabs, Merchants
from social.models import Likes

from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.views.decorators.http import require_POST


def user_is_normal_user(user):
    return isinstance(user, Users) and user.is_normal_user()


def do_logout(request):
    logout(request)
    return redirect('/')


def do_register(request):
    if request.method == 'POST':
        if 'facebookId' in request.POST:
            fbid = request.POST['facebookId']
            try:
                user = Users.objects.get(fbid__exact=fbid)
            except Users.DoesNotExist:
                bday = request.POST['birth']
                bday = bday[6:] + '-' + bday[0:2] + '-' + bday[3:5]
                user = Users.objects.create_user(fbid, fbid, bday,
                                                 email=request.POST['email'],
                                                 location=request.POST['location'],
                                                 first_name=request.POST['name'],
                                                 last_name=request.POST['lastName'],
                                                 gender=request.POST['gender'])
            if user:
                user = authenticate(username=fbid, password=fbid)
                if not user:
                    return HttpResponseBadRequest()
                login(request, user)
                return redirect('/')
            else:
                print 'LOG: No se pudo crear el usuario'
        else:
            return HttpResponseBadRequest()

    c = {}
    c.update(csrf(request))
    return render_to_response('register.html', c, context_instance=RequestContext(request))


@user_passes_test(user_is_normal_user, login_url='/logout')
def home(request, slug=None):
    categories = GiftcardCategory.objects.all()
    data = {}
    if slug:
        category = GiftcardCategory.objects.get(slug__exact=slug)
        products = Giftcard.objects.filter(category__exact=category.id)
        data = {
            'this_category': category,
        }
    else:
        products = Giftcard.objects.all()
    all_product_len = Giftcard.objects.count()

    if request.user.is_authenticated:
        for product in products:
            product.get_friend_likes = Likes.get_likes_from_friends(request.user.fbid,
                                                                    product.id)
            product.get_own_like = Likes.does_user_likes(request.user.fbid,
                                                         product.id)

    data.update({
        'categories': categories,
        'products': products,
        'all_products_len': all_product_len,
    })
    return render_to_response('giftcard.html', data,
                              context_instance=RequestContext(request))


@user_passes_test(user_is_normal_user, login_url='/logout')
def giftcard_detail(request, gift_id):
    giftcard = Giftcard.objects.get(pk=gift_id)
    likes = Likes.get_giftcard_likes(gift_id)
    friends = 0
    data = {
        'giftcard': giftcard,
        'likes': likes,
        'friends': friends
    }
    return render_to_response('giftcard_details.html', data,
                              context_instance=RequestContext(request))


@user_passes_test(user_is_normal_user, login_url='/logout')
def giftcard_custom(request, gift_id):
    giftcard = Giftcard.objects.get(pk=gift_id)
    style = GiftcardDesign.objects.filter(status='publish')
    likes = 0
    friends = 0
    data = {
        'giftcard': giftcard,
        'likes': likes,
        'friends': friends,
        'styles': style,
    }

    return render_to_response('giftcard_custom.html', data,
                              context_instance=RequestContext(request))


@login_required
@user_passes_test(user_is_normal_user, login_url='/logout')
def user(request):
    data = {}
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
        customer = Users.objects.create_inactive_user(email_to)
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
        'hash': uuid.split('-')[0]

    }

    return render_to_response('product_show.html', data,
                              context_instance=RequestContext(request))


@user_passes_test(user_is_normal_user, login_url='/logout')
def partner_info(request, merchant_slug):
    merchant = Merchants.objects.get(slug__exact=merchant_slug)
    tabs = MerchantTabs.objects.filter(parent_id=merchant.id)
    product = Giftcard.objects.filter(merchant=merchant.id)
    data = {
        'merchant': merchant,
        'products': product,
        'tabs': tabs,
    }

    return render_to_response('partner_info.html', data,
                              context_instance=RequestContext(request))

def response_not_found(request):
    return render_to_response('404.html')

def search(request):
    return render_to_response('search.html')

def page_who_we_are(request):
    return render_to_response('page_who_we_are.html')

def page_who_its_work(request):
    return render_to_response('page_who_its_work.html')

def page_faq(request):
    return render_to_response('page_faq.html')

def page_enterprise(request):
    return render_to_response('page_enterprise.html')

def page_contact(request):
    return render_to_response('page_contact.html')

def page_terms(request):
    return render_to_response('page_terms.html')

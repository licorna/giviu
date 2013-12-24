from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render_to_response, redirect
from django.core.context_processors import csrf
from django.contrib.auth import authenticate, login, logout
from django.template import RequestContext
from models import (
    GiftcardCategory, Products, Likes, Merchants, UserFriends, GiftcardStyle,
    Users
)
from hashlib import md5


def do_login(request, fbid=None):
    #if request.user.is_authenticated():
    #    # if user is already logged in, return to home
    #    return redirect('/')

    if fbid:
        user = authenticate(username=fbid, password=fbid)
        if user is not None:
            login(request, user)
            return True

    return False


def do_logout(request):
    logout(request)
    return redirect('/')

def do_register(request):
    if request.method == 'POST':
        if 'facebookId' in request.POST:
            fbid = request.POST['facebookId']
            try:
                user = Users.objects.get(fb_id__exact=fbid)
            except Users.DoesNotExist:
                print 'creando un nuevo usuario'
                bday = request.POST['birth']
                user = Users.objects.create_user(fbid, fbid, bday)
            if user:
                user = authenticate(username=fbid, password=fbid)
                if not user:
                    return HttpResponseBadRequest()
                login(request, user)
                return redirect('/')
            else:
                print 'no se pudo crear el usuario siii'
        else:
            return HttpResponseBadRequest()

    c = {}
    c.update(csrf(request))
    return render_to_response('register.html', c, context_instance=RequestContext(request))

def attach_merchant_to_products(products):
    for p in products:
        p.merchant = Merchants.objects.get(pk=int(p.merchant_id))
    return products

def home(request, slug=None):
    categories = GiftcardCategory.objects.all()
    data = {}
    if slug:
        category = GiftcardCategory.objects.get(slug__exact=slug)
        products = Products.objects.filter(category__exact=category.giftcardcategory_id)
        data = {
            'this_category': category,
        }
    else:
        products = Products.objects.all()
    all_product_len = Products.objects.count()
    products = attach_merchant_to_products(products)
    data.update({
        'categories': categories,
        'products': products,
        'all_products_len': all_product_len,
    })
    return render_to_response('giftcard.html', data, context_instance=RequestContext(request))


def giftcard_detail(request, gift_id):
    product = Products.objects.get(pk=gift_id)
    if product.kind == '1':
        product.price = product.price.split(',')
        product.merchant = Merchants.objects.get(pk=product.merchant_id)
    try:
        likes = Likes.objects.get(pk=gift_id)
        friends = UserFriends.objects.filter(user_friend_fb_id__exact=likes.like_user_fb_id)
    except Likes.DoesNotExist:
        likes = 0
        friends = 0
    data = {
        'product': product,
        'likes': likes,
        'friends': friends,
    }
    return render_to_response('giftcard_details.html', data, context_instance=RequestContext(request))


def giftcard_custom(request, gift_id):
    product = Products.objects.get(pk=gift_id)
    style = GiftcardStyle.objects.all()
    if product.kind == '1':
        product.price = product.price.split(',')
        product.merchant = Merchants.objects.get(pk=product.merchant_id)
    try:
        likes = Likes.objects.get(pk=gift_id)
        friends = UserFriends.objects.filter(user_friend_fb_id__exact=likes.like_user_fb_id)
    except Likes.DoesNotExist:
        likes = 0
        friends = 0
    data = {
        'product': product,
        'likes': likes,
        'friends': friends,
        'styles': style,
    }
    return render_to_response('giftcard_custom.html', data, context_instance=RequestContext(request))


def giftcard_confirmation(request):
    if request.method != 'POST':
        return redirect('/')

    product = Products.objects.get(pk=int(request.POST['product-id']))
    merchant = Merchants.objects.get(pk=int(request.POST['product-merchant-id']))

    data = {
        'send_to': request.POST['send-to'],
        'email_to': request.POST['email-to'],
        'send_date': request.POST['send-date'],
        'comment': request.POST['comment'],
        'price': request.POST['product-price'],
        'giftcard_design': request.POST['giftcard-design'],
        'product': product,
        'merchant': merchant
    }
    data.update(csrf(request))

    return render_to_response('pay_confirmation.html', data, context_instance=RequestContext(request))

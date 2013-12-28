from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render_to_response, redirect
from django.core.context_processors import csrf
from django.contrib.auth import authenticate, login, logout
from django.template import RequestContext
from models import (
    GiftcardCategory, Giftcard, Likes, Merchants, Friend, GiftcardDesign,
    Users,
)
from hashlib import md5


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
                bday = bday[6:] + '-' + bday[3:5] + '-' + bday[0:2]
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
    data.update({
        'categories': categories,
        'products': products,
        'all_products_len': all_product_len,
    })
    return render_to_response('giftcard.html', data, context_instance=RequestContext(request))


def giftcard_detail(request, gift_id):
    product = Giftcard.objects.get(pk=gift_id)
    if product.kind == '1':
        product.price = product.price.split(',')
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
    product = Giftcard.objects.get(pk=gift_id)
    style = GiftcardDesign.objects.all()
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

    product = Giftcard.objects.get(pk=int(request.POST['product-id']))
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

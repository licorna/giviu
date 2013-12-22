from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.core.context_processors import csrf
from django.contrib.auth import authenticate, login, logout
from django.template import RequestContext
from models import GiftcardCategory, Products, Likes, Merchants, UserFriends, GiftcardStyle
from datetime import datetime
from hashlib import md5

def do_login(request):
    if request.user.is_authenticated():
        # if user is already logged in, return to home
        return redirect('/')
    c = {}
    c.update(csrf(request))
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['pass']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('/')
        else:
            # TODO: improve way of user alerting.
            return redirect('/login?message=invalid')

    # TODO: same here, improve this ugly snippet
    if 'message' in request.GET:
        c['message'] = request.GET['message']
    return render_to_response('login.html', c, context_instance=RequestContext(request))

def do_logout(request):
    logout(request)
    return redirect('/')

def do_register(request):
    return render_to_response('register.html')

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
    date = datetime.now()
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
        'today': date.strftime("%Y-%m-%d")
    }
    return render_to_response('giftcard_custom.html', data, context_instance=RequestContext(request))

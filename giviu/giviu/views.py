from django.http import HttpResponseBadRequest
from django.shortcuts import render_to_response, redirect
from django.core.context_processors import csrf
from django.contrib.auth import authenticate, login, logout
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from models import (
    GiftcardCategory, Giftcard, Likes, GiftcardDesign,
    Users, Product
)

from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.views.decorators.http import require_POST


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
    return render_to_response('giftcard.html', data,
                              context_instance=RequestContext(request))


def giftcard_detail(request, gift_id):
    giftcard = Giftcard.objects.get(pk=gift_id)
    try:
        likes = Likes.objects.get(pk=gift_id)
    except Likes.DoesNotExist:
        likes = 0
        friends = 0
    data = {
        'giftcard': giftcard,
        'likes': likes,
        'friends': friends
    }
    return render_to_response('giftcard_details.html', data, context_instance=RequestContext(request))


def giftcard_custom(request, gift_id):
    giftcard = Giftcard.objects.get(pk=gift_id)
    style = GiftcardDesign.objects.all()
    try:
        likes = Likes.objects.get(pk=gift_id)
        friends = UserFriends.objects.filter(user_friend_fb_id__exact=likes.like_user_fb_id)
    except Likes.DoesNotExist:
        likes = 0
        friends = 0
    data = {
        'giftcard': giftcard,
        'likes': likes,
        'friends': friends,
        'styles': style,
    }

    return render_to_response('giftcard_custom.html', data, context_instance=RequestContext(request))


def user(request):
    data = {}
    return render_to_response('user.html',
                              data,
                              context_instance=RequestContext(request))


def sent(request):
    data = {}
    return render_to_response('user_sent.html',
                              data,
                              context_instance=RequestContext(request))


def calendar(request):
    data = {}
    return render_to_response('user_calendar.html',
                              data,
                              context_instance=RequestContext(request))


@require_POST
@login_required
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

    product = Product(giftcard_from=request.user,
                      giftcard_to_email=email_to,
                      giftcard_to_name=name_to,
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
        'trx_id': trx_id
    }
    data.update(csrf(request))

    return render_to_response('checkout_confirmation.html',
                              data,
                              context_instance=RequestContext(request))


def giftcard_error(request):
    return render_to_response('giftcard_error.html')

def giftcard_success(request):
    return render_to_response('giftcard_success.html')

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

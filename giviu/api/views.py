from django.http import (HttpResponse, HttpResponseBadRequest,
                         HttpResponseNotFound)
from django.views.decorators.csrf import csrf_exempt
from giviu.models import Users, Product, Giftcard
from api.models import ApiClientId
from social.models import Likes
from datetime import datetime
import json


def version(request):
    data = {}
    data['version'] = '1'
    data['description'] = 'First API version'
    data['url'] = 'https://www.giviu.com/api/v1'

    return HttpResponse(json.dumps(data), content_type='application/json')


def user_exists_by_fbid(request, fbid):
    try:
        user = Users.objects.get(fbid__exact=fbid)
    except Users.DoesNotExist:
        return HttpResponse(
            json.dumps({'message': 'Not a corresponding user for this FB id.'}),
            content_type='application/json',
            status=404
        )
    return HttpResponse(
        json.dumps({'user_id': user.id}),
        content_type='application/json',
        status=200
    )


@csrf_exempt
def get_sales_by_service(request, merchant_id):
    if 'client_id' not in request.GET:
        return HttpResponseBadRequest()

    giftcards = Giftcard.objects.filter(merchant=merchant_id)
    data = {}
    for giftcard in giftcards:
        data[giftcard.id] = {
            'title': giftcard.title,
            'sold_qty': giftcard.sold_quantity
        }

    return HttpResponse(
        json.dumps(data),
        content_type='application/json',
        status=200
    )


@csrf_exempt
def validate_giftcard(request, giftcard):
    if 'client_id' not in request.GET:
        return HttpResponseBadRequest()
    client_id = request.GET['client_id']
    try:
        client = ApiClientId.objects.get(client_id=client_id)
    except ApiClientId.DoesNotExist:
        return HttpResponseBadRequest()

    try:
        product = Product.objects.get(validation_code__exact=giftcard)
    except Product.DoesNotExist:
        return HttpResponse(
            json.dumps({'message': 'Does not exist'}),
            content_type='application/json',
            status=404
        )

    if product.giftcard.merchant != client.merchant:
        return HttpResponseNotFound()

    if request.method == 'PUT':
        if product.validated == 0:
            product.validated = 1
            product.validation_date = datetime.now()
            product.save()
            response = {'status': 'The giftcard has been validated'}
            status = 200
        else:
            response = {
                'status': 'The giftcard has already been validated',
                'validation_date': product.validation_date.isoformat()
            }
            status = 400
        return HttpResponse(json.dumps(response),
                            content_type='application/json',
                            status=status)

    data = {
        'id': giftcard,
        'from': product.giftcard_from.email,
        'to': product.giftcard_to.get_full_name(),
        'already_validated': product.validated == 1,
        'giftcard_price': int(product.price),
        'product': product.giftcard.title,
    }
    if product.validated == 1:
        data['validation_date'] = product.validation_date.isoformat()

    return HttpResponse(
        json.dumps({'giftcard': data}),
        content_type='application/json',
        status=200
    )


@csrf_exempt
def add_gf_like(request, user, giftcard):
    Likes.add_giftcard_like(user, giftcard)
    return HttpResponse()


def get_gf_like(request, user, giftcard):
    response = Likes.get_likes_from_friends(user, giftcard)
    data = {
        'user': {
            'fbid': user,
            'friends_like': response
        }
    }
    return HttpResponse(json.dumps(data), content_type='application/json', status_code=200)


@csrf_exempt
def add_friends_from_facebook(request):
    data = json.loads(request.POST)
    response = Likes.add_users_to_social(data)
    if response:
        return HttpResponse('{"status":"success"}', status_code=200)

    return HttpResponseBadRequest()

from django.http import HttpResponse
from giviu.models import Users, Product
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


def validate_giftcard(request, giftcard):
    try:
        product = Product.objects.get(validation_code__exact=giftcard)
    except Product.DoesNotExist:
        return HttpResponse(
            json.dumps({'message': 'Does not exist'}),
            content_type='application/json',
            status=404
        )
    if request.method == 'POST':
        if product.validated == 0:
            product.validated = 1
            product.save()
            response = {'status': 'validated'}
            status = 200
        else:
            response = {'status': 'already validated'}
            status = 400
        return HttpResponse(json.dumps(response),
                            content_type='application/json',
                            status=status)

    data = {
        'uuid': giftcard,
        'from': product.giftcard_from.email,
        'to': product.giftcard_to.email,
        'already_validated': product.validated == 1,
        'giftcard-price': int(product.price),
    }

    return HttpResponse(
        json.dumps({'giftcard': data}),
        content_type='application/json',
        status=200
    )

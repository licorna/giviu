from django.http import HttpResponse
from django.shortcuts import render_to_response
from models import GiftcardCategory, Products, Likes, Merchants

def home(request):
    categories = GiftcardCategory.objects.all()
    products = Products.objects.all()
    for p in products:
        if p.type_ == '1':
            p.price = p.price.split(',')
        # FIXIT: Following reference should be automatic if model had coherent references.
        p.merchant = Merchants.objects.get(pk=int(p.merchant_id))
    data = {
        'categories': categories,
        'products': products
    }
    return render_to_response('giftcard_category.html', data)


def giftcard_detail(request, gift_id):
    product = Products.objects.get(pk=gift_id)
    if product.type_ == '1':
        product.price = product.price.split(',')
        product.merchant = Merchants.objects.get(pk=product.merchant_id)
    likes = Likes.objects.filter(likes_id__exact=gift_id)
    # friends = # TODO
    data = {
        'product': product,
        'likes': likes
    }
    return render_to_response('giftcard_details.html', data)

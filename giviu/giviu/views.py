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
    return render_to_response('giftcard.html', data)


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

def giftcard_category(request, slug):
    print slug
    category = GiftcardCategory.objects.get(slug__exact=slug)
    products_this = Products.objects.filter(category__exact=category.giftcardcategory_id)
    for p in products_this:
        if p.type_ == '1':
            p.price = p.price.split(',')
        # FIXIT: Following reference should be automatic if model had coherent references.
        p.merchant = Merchants.objects.get(pk=int(p.merchant_id))
    products_all = Products.objects.all()
    categories = GiftcardCategory.objects.all()
    data = {
        'slug': slug,
        'title': category.name,
        'products': products_this,
        'products_all': products_all,
        'categories': categories
    }
    return render_to_response('giftcard_category.html', data)

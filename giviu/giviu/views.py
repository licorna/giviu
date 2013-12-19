from django.http import HttpResponse
from django.shortcuts import render_to_response
from models import GiftcardCategory, Products

def home(request):
    categories = GiftcardCategory.objects.all()
    products = Products.objects.all()
    for p in products:
        if p.type_ == '1':
            p.price = p.price.split(',')
    data = {
        'categories': categories,
        'products': products
    }
    return render_to_response('giftcard_category.html', data)

from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.http import HttpResponseBadRequest, HttpResponse, HttpResponseNotFound
from django.contrib.auth import authenticate, login
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from giviu.models import Users, Giftcard, Product, CustomerInfo
import json


def do_login(request):
    data = {}
    if request.method == 'POST':
        if 'email' not in request.POST or 'password' not in request.POST:
            return HttpResponseBadRequest()
        email = request.POST['email']
        password = request.POST['password']

        try:
            user = Users.objects.get(email__exact=email)
            print 'he encotrado el usuario'
        except Users.DoesNotExist:
            print 'el usuario no existe!!!'
            data = {
                'message': 'Usuario o contrase&ntilde;a incorrectos'
            }
            return render_to_response('login_merchant.html', data,
                                      context_instance=RequestContext(request))
        if user:
            print 'a punto de autenticar el usuario'
            user = authenticate(username=email, password=password)
            if not user:
                print 'usuario no se pudo autenticar'
                return HttpResponseBadRequest()
            login(request, user)
            print 'usuario logueado'
            return redirect('/merchant/home')

    return render_to_response('login_merchant.html',
                              data, context_instance=RequestContext(request))


@login_required
def home(request):
    if not request.user.is_merchant:
        return HttpResponse('Restringido a merchants')

    merchant = request.user.merchant
    products = Product.objects.filter(giftcard__merchant=merchant,
                                      state='RESPONSE_FROM_PP_SUCCESS')
    products_validated_qty = len(filter(lambda x: x.validated, products))
    products_total_sold = reduce(lambda x, y: x+y, [int(p.price) for p in products], 0)
    client_id = merchant.get_api_client_id()
    data = {
        'products': products,
        'products_validated_qty': products_validated_qty,
        'products_to_validate_qty': len(products) - products_validated_qty,
        'total_sold': products_total_sold,
        'client_id': client_id
    }
    return render_to_response('home.html', data,
                              context_instance=RequestContext(request))


def validate(request):
    merchant = request.user.merchant
    client_id = merchant.get_api_client_id()
    data = {
        'client_id': client_id,
    }
    return render_to_response('validate.html', data,
                              context_instance=RequestContext(request))


def customers(request):
    customers = CustomerInfo.objects.filter(merchant=request.user.merchant)
    data = {
        'customers': customers
    }
    return render_to_response('customers.html', data,
                              context_instance=RequestContext(request))


def customer_profile(request, customer_id):
    try:
        customer = CustomerInfo.objects.get(pk=customer_id)
    except CustomerInfo.DoesNotExist:
        return HttpResponseNotFound()

    products = Product.objects.filter(giftcard_to=customer.user,
                                      state='RESPONSE_FROM_PP_SUCCESS')

    data = {
        'customer': customer,
        'products': products
    }

    return render_to_response('customer_profile.html', data,
                              context_instance=RequestContext(request))


def customer_edit(request, customer_id):
    customer = get_object_or_404(CustomerInfo, pk=customer_id)
    if request.method == 'POST':
        details = {}
        for k, v in request.POST.iteritems():
            details[k] = v
        customer.data = json.dumps(details)
        customer.save()

    try:
        customer_data = json.loads(customer.data)
    except ValueError:
        customer_data = {}
    data = {
        'customer': customer,
        'customer_data': customer_data
    }

    return render_to_response('customer_edit.html', data,
                              context_instance=RequestContext(request))


def users(request):
    data = {}

    return render_to_response('users.html')

def user_profile(request):
    data = {}

    return render_to_response('user_profile.html')

def user_new(request):
    data = {}

    return render_to_response('user_new.html')

from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.http import HttpResponseNotFound
from django.contrib.auth import authenticate, login
from django.template import RequestContext
from django.contrib.auth.decorators import user_passes_test
from giviu.models import Users, Product, CustomerInfo
import json


def do_login(request):
    def error():
        data = {
            'error': True,
            'message': 'Usuario o contrase&ntilde;a incorrectos'
        }
        return render_to_response('login_merchant.html', data,
                                  context_instance=RequestContext(request))

    if request.method == 'POST':
        if 'email' not in request.POST or 'password' not in request.POST:
            return error()
        email = request.POST['email']
        password = request.POST['password']

        try:
            user = Users.objects.get(email=email)
        except Users.DoesNotExist:
            return error()

        if user:
            user = authenticate(username=email, password=password)
            if not user:
                return error()
            login(request, user)
            return redirect('/merchant/home')

    return render_to_response('login_merchant.html', {},
                              context_instance=RequestContext(request))


@user_passes_test(lambda u: isinstance(u, Users) and u.is_merchant,
                  login_url='/merchant/login')
def home(request):
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


@user_passes_test(lambda u: isinstance(u, Users) and u.is_merchant,
                  login_url='/merchant/login')
def validate(request):
    return render_to_response('validate.html', {},
                              context_instance=RequestContext(request))


@user_passes_test(lambda u: isinstance(u, Users) and u.is_merchant,
                  login_url='/merchant/login')
def customers(request):
    customers = CustomerInfo.objects.filter(merchant=request.user.merchant)
    data = {
        'customers': customers
    }
    return render_to_response('customers.html', data,
                              context_instance=RequestContext(request))


@user_passes_test(lambda u: isinstance(u, Users) and u.is_merchant,
                  login_url='/merchant/login')
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


@user_passes_test(lambda u: isinstance(u, Users) and u.is_merchant,
                  login_url='/merchant/login')
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

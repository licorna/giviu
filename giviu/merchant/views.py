from django.shortcuts import render_to_response, redirect
from django.http import HttpResponseBadRequest, HttpResponse
from django.contrib.auth import authenticate, login
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from giviu.models import Users, Giftcard, Product


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
    products_total_sold = reduce(lambda x, y: x+y, [int(p.price) for p in products])
    data = {
        'products': products,
        'products_validated_qty': products_validated_qty,
        'products_to_validate_qty': len(products) - products_validated_qty,
        'total_sold': products_total_sold
    }
    return render_to_response('home.html', data,
                              context_instance=RequestContext(request))


def validate(request):
    return render_to_response('validate.html', {},
                              context_instance=RequestContext(request))


def customers(request):
    customers = request.user.merchant.get_customers()
    data = {
        'customers': customers
    }
    return render_to_response('customers.html', data,
                              context_instance=RequestContext(request))

def customer_profile(request):
    data = {}

    return render_to_response('customer_profile.html')

def customer_edit(request):
    data = {}

    return render_to_response('customer_edit.html')

def users(request):
    data = {}

    return render_to_response('users.html')

def user_profile(request):
    data = {}

    return render_to_response('user_profile.html')

def user_new(request):
    data = {}

    return render_to_response('user_new.html')

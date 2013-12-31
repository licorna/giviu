from django.shortcuts import render_to_response

# Create your views here.

def login(request):
    data = {}

    return render_to_response('login_merchant.html')

def home(request):
    data = {}

    return render_to_response('home.html')

def validate(request):
    data = {}

    return render_to_response('validate.html')

def customers(request):
    data = {}

    return render_to_response('customers.html')

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

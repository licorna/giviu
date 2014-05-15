from django.http import HttpResponseBadRequest
from django.shortcuts import (render_to_response,
                              redirect)
from django.core.context_processors import csrf
from django.contrib.auth import authenticate, login as login_auth
from django.contrib import messages
from django.template import RequestContext
from django.views.decorators.http import (require_POST,
                                          require_GET)
import requests
import urllib
import cgi
import json
from giviu.models import Users
from utils import (connect, create_token_for_email_registration,
                   send_mail_with_registration_token)

def login(request):
    print 'login'
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        print 'autenticando a ' + email + ', ' + password
        user = Users.objects.get(email=email)
        if user and user.is_active:
            user = authenticate(username=email, password=password)
            if not user:
                return HttpResponseBadRequest()
            login_auth(request, user)
            return redirect('/')

    args = dict(client_id='880085325341796',
                redirect_uri='http://dev.giviu.com:8000/login/fbregister')
    facebook_login_url = 'https://graph.facebook.com/oauth/authorize?'
    facebook_login_url += urllib.urlencode(args)
    print facebook_login_url
    data = {'facebook_login_url': facebook_login_url}
    data.update(csrf(request))
    return render_to_response('register.html',
                              data,
                              context_instance=RequestContext(request))

def generate_random_string():
    import random
    import string
    val = []
    for i in range(10):
        val.append(random.choice(string.ascii_letters))

    return ''.join(val)

def fbregister(request):
    if request.GET.get('code'):
        print 'got response from facebook'
        args = dict(client_secret='24dbfca03a8137df6ddd8e6725d4e2e5',
                    code=request.GET.get('code'),
                    redirect_uri='http://dev.giviu.com:8000/login/fbregister',
                    client_id='880085325341796',
                    facebook_scope='email')
        r = requests.get('https://graph.facebook.com/oauth/access_token',
                         params=args)

        access_token = cgi.parse_qs(r.text)['access_token'][0]
        args = dict(access_token=access_token)
        profile = requests.get('https://graph.facebook.com/me', params=args)
        profile = json.loads(profile.text)
        print profile
        fbid = profile['id']
        if 'email' in profile:
            email = profile['email']
        else:
            email =  'sebastian+' + generate_random_string() + '@giviu.com'
        first_name = profile['first_name']
        last_name = profile['last_name']
        gender = profile['gender']
        try:
            user = Users.objects.get(fbid=fbid)
        except Users.DoesNotExist:
            user = Users.objects.create_user(fbid,
                                             fbid,
                                             None,
                                             email=email,
                                             first_name=first_name,
                                             last_name=last_name)
        user = authenticate(username=fbid, password=fbid)
        if not user:
            return HttpResponseBadRequest()
        login_auth(request, user)
        return redirect('/')

    return HttpResponseBadRequest()

@require_POST
def email_register(request):
    print ' solicitud *** '
    print request.POST
    if request.method == 'POST':
        req = frozenset(('name', 'email', 'passwd1', 'passwd2'))
        if req <= frozenset(request.POST):
            email = request.POST.get('email')
            name = request.POST.get('name')
            passwd = request.POST.get('passwd1')
            try:
                user = Users.objects.get(email=email)
            except Users.DoesNotExist:
                token = create_token_for_email_registration(email)
                user = Users.objects.create_user(email,
                                                 passwd,
                                                 None,
                                                 email=email,
                                                 first_name=name)
                user.is_active = 0
                user.save()
                send_mail_with_registration_token(email, token)
                messages.add_message(request, messages.INFO, 'Please check Inbox.')
                return redirect('/')
    return HttpResponseBadRequest('shaa')


@require_GET
def email_validate(request, token):
    cnx = connect()
    reg = cnx.reg_token.find_one({'token': token, 'used': False})
    if reg:
        email = reg['email']
        cnx.reg_token.update({'token': token},
                             {'$set': {'used': True}})
        user = Users.objects.get(email=email)
        user.is_active = 1
        user.save()
        messages.add_message(request, messages.INFO, 'Email Validated, please login.')
        return redirect('base_login')

    return HttpResponseBadRequest()

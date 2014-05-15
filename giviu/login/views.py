# -*- coding: utf-8 -*-

from django.http import HttpResponseBadRequest
from django.shortcuts import (render_to_response,
                              redirect)
from django.core.context_processors import csrf
from django.contrib.auth import authenticate, login as login_auth
from django.contrib import messages
from django.template import RequestContext
from django.conf import settings
from django.core.urlresolvers import reverse
from django.views.decorators.http import (require_POST,
                                          require_GET)
import requests
import urllib
import cgi
import json
from giviu.models import Users
from utils import (connect, create_token_for_email_registration,
                   send_mail_with_registration_token)
import logging
logger = logging.getLogger('giviu')


def build_redirect_uri(request, current):
    redirect_uri = 'https://' if request.is_secure() else 'http://'
    redirect_uri += request.get_host() + reverse(current)
    return redirect_uri


def build_facebook_login_url(request):
    args = dict(client_id=settings.FBAPP_ID,
                redirect_uri=build_redirect_uri(request, 'fbregister'),
                scope=settings.FBAPP_SCOPE)
    facebook_login_url = settings.FBAPP_LOGIN_URL + '?'
    facebook_login_url += urllib.urlencode(args)
    return facebook_login_url


def login(request):
    if request.method == 'POST':
        if 'email' not in request.POST or 'password' not in request.POST:
            return HttpResponseBadRequest()
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user = Users.objects.get(email=email)
        except Users.DoesNotExist:
            messages.add_message(request, messages.INFO,
                                 'Usuario o contraseña incorrectos.')
            return redirect('base_login')
        if user and user.is_active:
            user = authenticate(username=email, password=password)
            if not user:
                messages.add_message(request, messages.INFO,
                                     'Usuario o contraseña incorrectos.')
                return redirect('base_login')
            login_auth(request, user)
            return redirect('/')
        else:
            messages.add_message(request, messages.INFO,
                                 'Usuario o contraseña incorrectos.')
            return redirect('base_login')

    data = {'facebook_login_url': build_facebook_login_url(request)}
    data.update(csrf(request))
    return render_to_response('register.html',
                              data,
                              context_instance=RequestContext(request))


def fbregister(request):
    if request.GET.get('code'):
        args = dict(client_secret=settings.FBAPP_SECRET,
                    code=request.GET.get('code'),
                    redirect_uri=build_redirect_uri(request, 'fbregister'),
                    client_id=settings.FBAPP_ID)
        r = requests.get(settings.FBAPP_ACCESS_TOKEN_URL,
                         params=args)

        access_token = cgi.parse_qs(r.text)
        if 'access_token' not in access_token:
            messages.add_message(request, messages.ERROR,
                                 'Ha ocurrido un error al intentar ingresar con tu cuenta de Facebook, inténtalo nuevamente.')
            return redirect('base_login')
        access_token = access_token['access_token'][0]
        args = dict(access_token=access_token,
                    scope=settings.FBAPP_SCOPE)
        profile = requests.get(settings.FBAPP_ME_URL, params=args)
        profile = json.loads(profile.text)
        fbid = profile['id']
        if 'email' in profile:
            email = profile['email']
        else:
            email = generate_random_string() + '@giviu.com'
        first_name = profile['first_name']
        last_name = profile['last_name']
        gender = profile['gender']
        birthday = profile['birthday']
        try:
            user = Users.objects.get(fbid=fbid)
        except Users.DoesNotExist:
            user = Users.objects.create_user(fbid,
                                             fbid,
                                             birthday,
                                             email=email,
                                             first_name=first_name,
                                             last_name=last_name)
        user = authenticate(username=fbid, password=fbid)
        if not user:
            messages.add_message(request, messages.ERROR, 'Ha ocurrido un error al intentar ingresar con tu cuenta de Facebook, inténtalo nuevamente.')
            return redirect('base_login')
        login_auth(request, user)
        return redirect('/')

    else:
        messages.add_message(request, messages.ERROR, 'Ha ocurrido un error al intentar ingresar con tu cuenta de Facebook, inténtalo nuevamente.')
        return redirect('base_login')

    return redirect('/')

@require_POST
def email_register(request):
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
                messages.add_message(request, messages.INFO, 'Recuerda que aun debes validar tu dirección de e-mail.')
                return redirect('/')

    return redirect('/')


@require_GET
def email_validate(request, token):
    cnx = connect()
    if not cnx:
        messages.add_message(request, messages.INFO, 'Error validando email. Por favor, intenta nuevamente.')
        logger.critical('Unable to connect to Mongo Engine.')
        return redirect('/')
    reg = cnx.reg_token.find_one({'token': token, 'used': False})
    if reg:
        email = reg['email']
        cnx.reg_token.update({'token': token},
                             {'$set': {'used': True}})
        user = Users.objects.get(email=email)
        user.is_active = 1
        user.save()
        messages.add_message(request, messages.INFO, 'Email validado. ¡Ahora puedes ingresar a Giviu!')
        return redirect('base_login')

    messages.add_message(request, messages.WARNING, 'Solicitud No Válida.')
    return redirect('base_login')

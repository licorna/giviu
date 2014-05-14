from django.http import HttpResponseBadRequest
from django.shortcuts import (render_to_response,
                              redirect)
from django.core.context_processors import csrf
from django.contrib.auth import authenticate, login as login_auth
from django.contrib import messages
from django.template import RequestContext
from django.views.decorators.http import (require_POST,
                                          require_GET)
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

    return render_to_response('register.html',
                              csrf(request),
                              context_instance=RequestContext(request))

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
                print 'creando usuario'
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

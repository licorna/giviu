from django.shortcuts import render_to_response
from django.http import HttpResponseBadRequest
from django.template import RequestContext
from django.contrib.auth.models import AnonymousUser
from landing.models import BetaRegisteredUser
from django.conf import settings
from datetime import datetime
from giviu.views import home as main_home


def home(request):

    data = {}
    if request.method == 'POST':
        if 'name' not in request.POST or 'email' not in request.POST:
            return HttpResponseBadRequest()
        try:
            real_ip = request.META['HTTP_X_FORWARDED_FOR']
        except KeyError:
            real_ip = request.META['REMOTE_ADDR']

        email = request.POST['email']
        name = request.POST['name']
        try:
            user = BetaRegisteredUser.objects.get(email__exact=email)
            data['user_already_exist'] = True
            return render_to_response('landing.html',
                                      data,
                                      context_instance=RequestContext(request))
        except BetaRegisteredUser.DoesNotExist:
            user = BetaRegisteredUser(
                email=email,
                name=name,
                ip=real_ip,
                comment=request.POST.get('comment', None)
            )
            user.save()
            data['user_created'] = True

    return render_to_response('landing.html',
                              data,
                              context_instance=RequestContext(request))

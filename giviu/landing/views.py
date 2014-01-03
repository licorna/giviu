from django.shortcuts import render_to_response
from django.http import HttpResponseBadRequest
from django.template import RequestContext
from landing.models import BetaRegisteredUser


def home(request):
    data = {}
    if request.method == 'POST':
        if 'name' not in request.POST or 'email' not in request.POST:
            return HttpResponseBadRequest()

        email = request.POST['email']
        name = request.POST['name']
        comment = ''
        if 'comment' in request.POST:
            comment = request.POST['comment']
        ip = request.META['REMOTE_ADDR']
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
                ip=ip,
                comment=comment
            )
            user.save()
            data['user_created'] = True

    return render_to_response('landing.html',
                              data,
                              context_instance=RequestContext(request))

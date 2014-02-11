from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.core.context_processors import csrf
from django.views.decorators.http import require_GET
from giviu.models import Users


@require_GET
def friend(request, code):
    user = get_object_or_404(Users, referer=code)

    c = {'referer': code,
         'referer_name': user.get_full_name(),
         'referer_fbid': user.fbid}
    c.update(csrf(request))
    return render_to_response('register.html', c,
                              context_instance=RequestContext(request))

from django.http import HttpResponse, HttpResponseBadRequest
import json
from django.conf import settings


def get_git_index_sha():
    return '57141b8'


def index(request):
    if request.META['REMOTE_ADDR'] != settings.BALANCER_ADDR:
        return HttpResponseBadRequest()

    data = {
        'git_index_sha': get_git_index_sha(),
        'database': {
            'name': settings.DATABASES['default']['NAME'],
            'host': settings.DATABASES['default']['HOST']
        },
        'status': 'ok'
    }
    return HttpResponse(json.dumps(data), content_type='application/json')

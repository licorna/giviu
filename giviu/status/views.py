from django.http import HttpResponse
import json
from django.conf import settings
import subprocess


def get_git_index_sha():
    return subprocess.check_output(['git', 'rev-parse', 'HEAD']).strip()


def status(request):
    data = {
        'database': {
            'name': settings.DATABASES['default']['NAME'],
            'host': settings.DATABASES['default']['HOST']
        },
        'status': 'ok'
    }
    return HttpResponse(json.dumps(data), content_type='application/json')


def version(request):
    data = {
        'git': {
            'commit': get_git_index_sha()
        }
    }
    return HttpResponse(json.dumps(data), content_type='application/json')

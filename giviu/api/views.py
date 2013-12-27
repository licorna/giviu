from django.shortcuts import render
from django.http import HttpResponse
from giviu.models import Users
import json

def version(request):
    data = {}
    data['version'] = '1'
    data['description'] = 'First API version'
    data['url'] = 'https://www.giviu.com/api/v1'

    return HttpResponse(json.dumps(data), content_type='application/json')

def user_exists_by_fbid(request, fbid):
    try:
        user = Users.objects.get(fbid__exact=fbid)
    except Users.DoesNotExist:
        return HttpResponse(
            json.dumps({'message': 'Not a corresponding user for this FB id.'}),
            content_type='application/json',
            status=404
        )
    return HttpResponse(
        json.dumps({'user_id': user.id}),
        content_type='application/json',
        status=200
    )

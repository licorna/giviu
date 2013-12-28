from django.shortcuts import render, redirect, render_to_response
from django.http import HttpResponseBadRequest
import random

def first_stage(request):
    if request.method != 'POST':
        return HttpResponseBadRequest()

    print request.POST

    if random.randint(0,10) == 6:
        data = {
            'additional_head': '<meta http-equiv="refresh" content="10; url=http://giviudev.dev:8000/giftcard/error" />'
        }
        return render_to_reponse('error.html', data)

    data = {
        'additional_head': '<meta http-equiv="refresh" content="10; url=http://giviudev.dev:8000/giftcard/success" />'
    }
    return render_to_response('success.html', data)

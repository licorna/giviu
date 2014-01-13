import requests
from django.conf import settings
import json


class Likes():
    ENDPOINT = '/friend'
    TIMEOUT = settings.SOCIAL['TIMEOUT']

    @staticmethod
    def get_giftcard_likes(giftcard_id, just_count=True):
        '''Will fetch all the likes a giftcard has'''
        condition = {
            "giftcard_likes": giftcard_id
        }
        url = settings.SOCIAL['ENDPOINT'] + Likes.ENDPOINT
        url += "?where=" + json.dumps(condition)
        headers = {
            'Accept': 'application/json'
        }

        try:
            response = requests.get(url, data={}, headers=headers,
                                    timeout=Likes.TIMEOUT)
        except requests.exceptions.RequestException:
            return 0 if just_count else None

        if response.status_code == 200:
            jres = response.json()
            if just_count:
                if '_items' in jres:
                    return len(jres['_items'])
                else:
                    return 0
            return jres['_items']

        if just_count:
            return 0
        return None

    @staticmethod
    def add_giftcard_like(user, giftcard):
        condition = '?where={"fbid":"%s"}' % (user,)
        url = settings.SOCIAL['ENDPOINT'] + Likes.ENDPOINT + condition
        headers = {
            'Accept': 'application/json'
        }

        try:
            response = requests.get(url, data={}, headers=headers,
                                    timeout=Likes.TIMEOUT)
        except requests.exceptions.RequestException:
            return None

        user_likes = []
        user_id = ''
        if response.status_code == 200:
            jres = response.json()
            if 'giftcard_likes' in jres['_items'][0]:
                user_likes = jres['_items'][0]['giftcard_likes']
            user_id = jres['_items'][0]['_id']
            user_likes.append(int(giftcard))

        url = settings.SOCIAL['ENDPOINT'] + Likes.ENDPOINT
        headers = {
            'Content-Type': 'application/json'
        }
        data = {
            'giftcard_likes': user_likes,
        }
        try:
            url = url + '/' + user_id
            response = requests.patch(url, data=json.dumps(data),
                                      headers=headers, timeout=Likes.TIMEOUT)
        except requests.exceptions.RequestException:
            return None

        if response.status_code == 200:
            return True
        return False

import requests
from django.conf import settings


class Likes():
    ENDPOINT = '/friend'
    TIMEOUT = settings.SOCIAL['TIMEOUT']

    @classmethod
    def get_giftcard_likes(cls, giftcard_id, just_count=True):
        condition = '?where={"giftcard_likes":%d}' % (giftcard_id,)
        url = settings.SOCIAL['ENDPOINT'] + Likes.ENDPOINT + condition
        print url
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

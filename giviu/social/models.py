import requests
from django.conf import settings
import json


class Likes():
    ENDPOINT = '/friend'
    TIMEOUT = settings.SOCIAL['TIMEOUT']

    @staticmethod
    def add_user_to_social(fbid, name, birthdate):
        '''Will add the new registered user to Social database'''
        print 'a punto de enviar solicitud tiiiii'
        url = settings.SOCIAL['ENDPOINT'] + Likes.ENDPOINT
        data = {
            'fbid': fbid,
            'first_name': name,
            'birthdate': birthdate,
            'giftcard_likes': [],
            'friend_of': []
        }
        headers = {
            'Content-Type': 'application/json'
        }
        try:
            response = requests.post(url, data=data, headers=headers)
        except requests.exceptions.RequestException, e:
            print e
            # TODO: IMPORTANTE:
            # ESTO SE DEBE LOGUEAR Y ALERTAR!!
            return False

        return response.status_code < 300

    @staticmethod
    def add_users_to_social(users):
        '''Add users from facebook response to Social'''
        print 'add_users_to_social'
        url = settings.SOCIAL['ENDPOINT'] + Likes.ENDPOINT
        headers = {'Content-Type': 'application/json'}
        try:
            response = requests.post(url, data=users, headers=headers)
        except requests.exceptions.RequestException:
            print 'error agregando usuarios'

        return response.text < 300

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
    def does_user_likes(user, giftcard):
        '''Returns True if user already likes giftcard,
        False on contrary.'''
        condition = {
            "giftcard_likes": giftcard,
            "fbid": user,
        }
        url = settings.SOCIAL['ENDPOINT'] + Likes.ENDPOINT
        url += '?where=' + json.dumps(condition)
        headers = {'Accept': 'application/json'}
        try:
            response = requests.get(url, headers=headers)
        except requests.exceptions.RequestException:
            return False

        if response.status_code == 200:
            jres = response.json()
            return len(jres['_items']) > 0

        return False

    @staticmethod
    def add_giftcard_like(user, giftcard):
        '''Adds a giftcard_like to given user/giftcard.'''
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
            if int(giftcard) not in user_likes:
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

    @staticmethod
    def get_social_user(fbid):
        '''Returns the full user Social object.'''
        condition = {
            "fbid": fbid,
        }
        url = settings.SOCIAL['ENDPOINT'] + Likes.ENDPOINT
        url += '?where=' + json.dumps(condition)
        headers = {
            'Accept': 'applicaton/json'
        }
        try:
            response = requests.get(url, headers=headers)
        except requests.exceptions.RequestException:
            return None

        return response.json()

    @staticmethod
    def get_likes_from_friends(fbid, giftcard):
        '''Returns a list of facebook ids of friends that liked
        the given giftcard.'''
        likes = []
        condition = {
            "fbid": fbid,
            "giftcard_likes": int(giftcard)
        }
        url = settings.SOCIAL['ENDPOINT'] + Likes.ENDPOINT
        url += '?where=' + json.dumps(condition)
        headers = {'Accept': 'application/json'}
        friends = Likes.get_social_user(fbid)['_items'][0]['friend_of']
        for friend in friends:
            condition = {
                "fbid": friend,
                "giftcard_likes": int(giftcard)
            }
            url = settings.SOCIAL['ENDPOINT'] + Likes.ENDPOINT
            url += '?where=' + json.dumps(condition)
            headers = {'Accept': 'application/json'}
            try:
                response = requests.get(url, headers=headers)
            except requests.exceptions.RequestException:
                # TODO: Loguear y reportar
                print 'error en Social'
            if response.status_code == 200:
                response = response.json()
                if len(response['_items']) > 0:
                    if giftcard in response['_items'][0]['giftcard_likes']:
                        likes.append(friend)

        return likes

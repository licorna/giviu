import requests
from django.conf import settings
import json
from collections import defaultdict
import re
import pymongo


class Likes():
    ENDPOINT = '/friend'
    TIMEOUT = settings.SOCIAL['TIMEOUT']

    @staticmethod
    def get_social_client():
        mongo = pymongo.MongoClient(settings.SOCIAL['MONGO_HOST'])
        return mongo.eve

    @staticmethod
    def add_user_to_social(fbid, name, birthday):
        '''Will add the new registered user to Social database'''
        url = settings.SOCIAL['ENDPOINT'] + Likes.ENDPOINT
        data = {
            'fbid': fbid,
            'first_name': name,
            'birthday': birthday,
            'giftcard_likes': [],
            'friend_of': []
        }
        headers = {
            'Content-Type': 'application/json'
        }
        try:
            response = requests.post(url, data=json.dumps(data), headers=headers)
        except requests.exceptions.RequestException, e:
            print e
            # TODO: IMPORTANTE:
            # ESTO SE DEBE LOGUEAR Y ALERTAR!!
            return False

        return response.status_code < 300

    @staticmethod
    def add_users_to_social(users, fbid):
        '''Add users from facebook response to Social'''
        str_user = '{"fbid":"%(id)s","birthday":"%(birthday)s","first_name":"%(name)s","friend_of":["' + fbid +'"]}'

        data = []
        friend_ids = []
        for user in users:
            if 'name' in user and len(user['name']) > 80:
                user['name'] = user['name'][:80]
            friend_ids.append(user['id'])
            ddict = defaultdict(str)
            ddict.update(user)
            data.append(str_user % ddict)

        client = Likes.get_social_client()
        for friend in friend_ids:
            Likes.add_facebook_friend(fbid, friend, client)

        url = settings.SOCIAL['ENDPOINT'] + Likes.ENDPOINT
        headers = {'Content-Type': 'application/json'}
        data = '[' + u','.join(data).encode('utf-8') + ']'

        try:
            print 'enviando solicitud'
            response = requests.post(url, data=data, headers=headers,
                                     timeout=Likes.TIMEOUT)
        except requests.exceptions.RequestException:
            print 'error al enviar usuarios.'
            # TODO: Log!
            pass

        if response.status_code == 200:
            jres = response.json()
            client = Likes.get_social_client()
            for friend in jres:
                if friend['status'] == 'ERR':
                    print friend
                    issues = friend['issues']
                    for issue in issues:
                        if 'not unique' in issue:
                            match = re.search("\'(\d+)\'", issue)
                            try:
                                friend_id = match.group(1)
                            except KeyError:
                                continue
                            print 'adding', friend_id, 'as friend of', fbid
                            Likes.add_facebook_friend(friend_id, fbid, client)

        print response.status_code
        return response.status_code < 300

    @staticmethod
    def add_facebook_friend(fbid, friend, client=None):
        if not client:
            client = Likes.get_social_client()

        result = client.friend.update({"fbid": fbid},
                                      {"$addToSet": {"friend_of": friend}})
        return result['updatedExisting'] and not result['err']

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
            return []

        try:
            result = response.json()
        except:
            return []
        return result

    @staticmethod
    def get_likes_from_friends(fbid, giftcard):
        '''Returns a list of facebook ids of friends that liked
        the given giftcard.'''
        client = Likes.get_social_client()
        result = client.friend.aggregate([
            {"$match": {"friend_of": fbid, "giftcard_likes": giftcard}},
            {"$group": {"_id": "$fbid"}}
        ])

        if len(result['result']) > 0:
            return [res.values()[0] for res in result['result']]

        return []

    @staticmethod
    def delete_metadata(data):
        del(data['_id'])
        del(data['created'])
        del(data['updated'])
        del(data['friend_of'])
        if 'giftcard_likes' in data:
            del(data['giftcard_likes'])
        return data

    @staticmethod
    def get_facebook_friends_birthdays(fbid):
        client = Likes.get_social_client()
        result = client.friend.find(
            {"friend_of": fbid})
        result = filter(lambda x: len(x['birthday']) > 0, result)
        result = map(Likes.delete_metadata, result)

        return result

    @staticmethod
    def add_close_facebook_friend(fbid, friend):
        client = Likes.get_social_client()
        result = client.friend.update({"fbid": fbid},
                                      {"$addToSet": {"close_friend": friend}})
        return result['updatedExisting'] and not result['err']

    @staticmethod
    def get_close_facebook_friends(fbid):
        client = Likes.get_social_client()
        result = client.friend.find({"fbid":fbid})
        try:
            close_friends = result[0]['close_friend']
        except KeyError:
            return []
        result = client.friend.find(
            {"fbid": {"$in": close_friends}}
        )

        return map(Likes.delete_metadata, result)

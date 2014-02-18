from django.conf import settings
import pymongo
import logging
logger = logging.getLogger('giviu')


def connect():
    try:
        mongo = pymongo.MongoClient(settings.SOCIAL['MONGO_HOST'])
    except pymongo.errors.ConnectionFailure:
        logger.critical('Unable to connect to social mongo on ' +
                        settings.SOCIAL['MONGO_HOST'])
        return None
    return mongo.eve


def get_external_codes_for_giftcard(giftcard):
    client = connect()
    if not client:
        return None

    ecode = client.external_codes.find_one({'giftcard_id': giftcard.id,
                                            'status': 'available'})
    client.external_codes.update({'_id': ecode['_id']},
                                 {'$set': {'status': 'used'}})
    return ecode.code

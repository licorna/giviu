import pymongo
from django.conf import settings
from datetime import datetime, timedelta
from uuid import uuid4
import logging
logger = logging.getLogger(__name__)


def get_credits_db():
    try:
        database = pymongo.MongoClient(settings.SOCIAL['CREDITS_MONGO_HOST']).credits
    except:
        logger.critical('Unable to connect to ' + settings.SOCIAL['CREDITS_MONGO_HOST'])
        return None

    return database.eve


def add_user_credits(fbid, amount, description, expiration=None):
    '''Adds amount to user credits'''
    db = get_credits_db()
    if not db:
        return False

    if not expiration:
        expiration = datetime.now() + timedelta(days=30)

    d = {
        'fbid': fbid,
        'amount': amount,
        'description': description,
        'expiration': expiration,
    }

    print d

    db.credits.insert(d)
    return True


def user_credits(fbid):
    '''Returns sum of total credits for user.'''
    db = get_credits_db()
    if not db:
        return {'status': 'no user credits', 'amount': 0}

    credits = db.credits.find({'fbid': fbid})
    if credits.count() == 0:
        return {'status': 'no user credits', 'amount': 0}

    sum = 0
    for credit in credits:
        sum += credit['amount']

    if sum == 0:
        return {'status': 'no user credits', 'amount': 0}

    return {'status': 'user has credits', 'amount': sum}


def mark_user_credits(fbid, amount):
    '''Mark user credits for future use. It is a blocking to disallow
    double use.'''
    db = get_credits_db()
    if not db:
        return False

    uuid = str(uuid4())
    d = {
        'fbid': fbid,
        'amount': -amount,
        'datetime': datetime.now(),
        'expiration': datetime.now() + timedelta(minutes=20),
        'status': 'marked',
        'uuid': uuid,
    }
    db.credits.insert(d)
    return True, uuid


def use_user_credits(fbid, amount):
    '''Mark user credits as used by adding additional negative values
    as credits also.'''
    db = get_credits_db()
    if not db:
        return {'status': 'no credits used', 'amount': 0}

    credits = user_credits(fbid)
    if credits['amount'] == 0:
        return {'status': 'no credits used', 'amount': 0}

    result, uuid = mark_user_credits(fbid, amount)
    if result is True:
        return {'status': 'credits blocked', 'uuid': uuid, 'amount': amount}

    return {'status': 'unable to block credits', 'amount': 0}


def finalize_use_user_credits(uuid, used=True):
    db = get_credits_db()
    if not db:
        return {'status': 'unable to finalize credits use'}

    if used:
        db.credits.update({'uuid': uuid}, {'$set': {'status': 'used'}})
    else:
        db.credits.remove({'uuid': uuid})

    return {'status': 'credits marked as used'}

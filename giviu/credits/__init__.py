import pymongo
from django.conf import settings
from datetime import datetime, timedelta
import random
from uuid import uuid4
from string import digits
from puntopagos import get_normalized_amount, now_rfc1123
import logging
logger = logging.getLogger('giviu')

CREDITS_AUTH_HEADER = 'CREDITS-'


def transaction_create_no_psp(amount):
    from giviu.models import PaymentTransaction
    amount = get_normalized_amount(amount)
    trx_id = ''.join(random.sample(digits, 10))
    current_datetime = now_rfc1123()
    payment_method = 'credits'
    token = str(uuid4())

    payment = PaymentTransaction(
        transaction_uuid=trx_id,
        origin_timestamp=current_datetime,
        auth_header=CREDITS_AUTH_HEADER + token,
        payment_method=payment_method,
        amount=amount,
        state='USING_CREDITS',
        psp_token=token,
    )
    payment.save()
    response = {'trx_id': trx_id,
                'token': token}
    return response, payment


def get_credits_db():
    try:
        database = pymongo.MongoClient(settings.SOCIAL['CREDITS_MONGO_HOST'])
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

    db.credits.insert(d)
    return True


def user_credits(fbid):
    '''Returns sum of total credits for user.'''
    db = get_credits_db()
    if not db:
        return {'status': 'no user credits', 'amount': 0}

    unmark_user_credits(fbid)

    credits = db.credits.find({'fbid': fbid})
    if credits.count() == 0:
        return {'status': 'no user credits', 'amount': 0}

    sum = 0
    for credit in credits:
        sum += credit['amount']

    if sum == 0:
        return {'status': 'no user available credits', 'amount': 0}

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
        'expiration': datetime.now() + timedelta(minutes=10),
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


def unmark_user_credits(fbid):
    db = get_credits_db()
    if not db:
        return False

    res = db.credits.remove({'fbid': fbid,
                             'status': 'marked',
                             'expiration': {'$lt': datetime.now()}})

    return res['n'] > 0


def add_user_referer(fbid, referral_fbid):
    db = get_credits_db()
    if not db:
        return False

    user_referral = db.referral.find_one({'fbid': fbid, 'used': False})
    if user_referral is None:
        db.referral.insert({
            'fbid': fbid,
            'referrals': [referral_fbid],
            'used': False,
        })
    else:
        db.referral.update({'_id': user_referral['_id']},
                           {'$addToSet': {'referrals': referral_fbid}})
        if len(user_referral['referrals']) >= 4:
            add_user_credits(fbid, 1000, '5 usuarios referidos y registrados.')
            db.referral.update({'_id': user_referral['_id']},
                               {'$set': {'used': True}})

    return True

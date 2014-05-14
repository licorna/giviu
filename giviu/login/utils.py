import pymongo
from django.conf import settings
from datetime import datetime, timedelta
from hashlib import sha224
from django.core.mail import EmailMultiAlternatives


def connect():
    try:
        mongo = pymongo.MongoClient(settings.SOCIAL['MONGO_HOST'])
    except pymongo.errors.ConnectionFailure:
        return None
    return mongo.eve


def create_token_for_email_registration(email):
    cnx = connect()
    expiration = datetime.now() + timedelta(hours=24)
    token = sha224(email + str(expiration.second)).hexdigest()
    cnx.reg_token.update({'email': email},
                         {'token': token,
                          'expiration': expiration,
                          'email': email,
                          'used': False},
                         upsert=True)

    return token


def send_mail_with_registration_token(email, token):
    content = '''Welcome to Giviu:<br/>
Validation URL: http://dev.giviu.com:8000/login/validate/%s
''' % (token, )
    if settings.DEBUG:
        email = settings.DEBUG_EMAIL_RECEIVER
    msg = EmailMultiAlternatives('Validate Email',
                                 content,
                                 settings.EMAIL_DEFAULT_FROM,
                                 [email])
    msg.send()

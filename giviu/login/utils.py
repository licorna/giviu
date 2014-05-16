import pymongo
from django.conf import settings
from datetime import datetime, timedelta
from hashlib import sha224
from django.core.mail import EmailMultiAlternatives
from django.template import Context
from django.template.loader import get_template


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


def send_mail_with_registration_token(name, email, activation_url):
    c = Context({'name': name,
                 'activation_url': activation_url})

    html_content = get_template('marketing_welcome_activation.html').render(c)

    if settings.DEBUG:
        email = settings.DEBUG_EMAIL_RECEIVER
    msg = EmailMultiAlternatives('Valida tu Email para Giviu.',
                                 html_content,
                                 settings.EMAIL_DEFAULT_FROM,
                                 [email])
    msg.attach_alternative(html_content, 'text/html')
    msg.send()

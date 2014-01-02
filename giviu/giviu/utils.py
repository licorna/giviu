from datetime import datetime, timedelta

MYSQL_DATE_FORMAT = '%Y-%m-%d'
MYSQL_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'


def get_today():
    return datetime.now().strftime(MYSQL_DATE_FORMAT)


def get_one_month():
    return (datetime.now() + timedelta(days=31)).strftime(MYSQL_DATE_FORMAT)


def get_now():
    return datetime.now().strftime(MYSQL_DATETIME_FORMAT)

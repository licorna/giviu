from datetime import datetime, timedelta

MYSQL_DATE_FORMAT = '%Y-%m-%d'

def get_today():
    return datetime.now().strftime(MYSQL_DATE_FORMAT)

def get_one_month():
    return (datetime.now() + timedelta(days=31)).strftime(MYSQL_DATE_FORMAT)

import base64
import hashlib


def calculate_hash(data, hashed_fields, password, hash_method='md5'):
    _line = u';'.join(map(str, [data.get(key) or '' for key in hashed_fields]))
    _line += u';{0}'.format(password)
    _hash = getattr(hashlib, hash_method)(bytes(_line.encode('utf-8')))
    _hash = base64.b64encode(_hash.digest())
    return _hash.decode('utf-8')


DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"


def format_dt(dt):
    return dt.strftime(DATETIME_FORMAT)

def parse_datetime(dt_string):
    from dateutil.parser import parse
    return parse(dt_string)




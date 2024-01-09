import calendar

import jwt
import api.models
from datetime import datetime
from graphql_jwt.settings import jwt_settings
    

def jwt_payload(user, context=None):
    jwt_datetime = datetime.utcnow() + jwt_settings.JWT_EXPIRATION_DELTA
    jwt_expires = int(jwt_datetime.timestamp())
    payload = {}
    payload['username'] = str(user.username)  # For library compatibility
    payload['sub'] = str(user.id)
    payload['sub_name'] = user.username
    payload['sub_email'] = user.email
    payload['exp'] = jwt_expires
    return payload


def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year,month)[1])
    return datetime(year, month, day, sourcedate.hour, sourcedate.minute, sourcedate.second, sourcedate.microsecond, sourcedate.tzinfo)

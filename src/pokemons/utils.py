import datetime

def get_current_timestamp():
    return datetime.datetime.now().replace(microsecond=0).isoformat()

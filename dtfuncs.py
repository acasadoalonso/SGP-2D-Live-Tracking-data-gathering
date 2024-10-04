from datetime import datetime, timezone

def aware_utcnow():
    return datetime.now(timezone.utc)

def aware_utcfromtimestamp(timestamp):
    return datetime.fromtimestamp(timestamp, timezone.utc)

def naive_utcnow():
    return aware_utcnow().replace(tzinfo=None)

def naive_utcfromtimestamp(timestamp):
    return aware_utcfromtimestamp(timestamp).replace(tzinfo=None)


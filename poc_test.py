from notifiers.providers.pushover import Pushover

data = {'title': 'bla', 'message': 'foo', 'user_key': 'uFMARdqgXPGXM6jx549jpT7Nk4Prn3'}
Pushover().notify(data)

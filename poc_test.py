from notifiers.providers.pushover import Pushover

data = {'title': 'bla', 'message': 'foo', 'user': 'uFMARdqgXPGXM6jx549jpT7Nk4Prn3', 'token': 'aPwSHwkLcNaavShxktBpgJH4bRWc3m'}
Pushover().notify(data)

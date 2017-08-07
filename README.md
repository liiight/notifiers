# Notifiers

The easiest way to send push notifications!

[![travis](https://img.shields.io/travis/liiight/notifiers/master.svg)](https://travis-ci.org/liiight/notifiers)  [![codecov](https://codecov.io/gh/liiight/notifiers/branch/master/graph/badge.svg)](https://codecov.io/gh/liiight/notifiers)  [![Join the chat at https://gitter.im/notifiers/Lobby](https://badges.gitter.im/notifiers/notifiers.svg)](https://gitter.im/notifiers/notifiers?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)


From python:
```python
>>> from notifiers import get_notifier

>>> pushover = get_notifer('pushover')
>>> pushover.notify(title='Foo', message='Bar', token='TOKEN')

```

## Setup
```
pip install notifiers
```

## Usage

Get a notifier:
```python
pushover = notifiers.get_notifer('pushover')
```
Or:
```python
pushover = notifiers.providers.Pushover()
```

Send a notification:
```python
pushover.notify(token='TOKEN', title='Foo', message='Bar')
```

Get notifier metadata:
```text
print(pushover.metadata)

{
    "url": "http://..."
    "description": "A Great notifier!"
    ..
}
```

## In the near future

- Many more providers
- CLI
- Environment variable support
- Docs

### Why python 3 only?

I wanted to avoid the whole unicode issue fiasco if possible, but there's not real constraint in adding python 2 support. If there's an overwhelming desire for this, i'll do it. Probably. 

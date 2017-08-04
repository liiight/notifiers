# Notifiers
Generic way to use notification services

[![travis](https://api.travis-ci.org/liiight/notifiers.png?branch=master)](https://travis-ci.org/liiight/notifiers)

From python:
```python
import notifiers

pushover = notifiers.get_notifer('pushover')
pushover.notify(title='Foo', message='Bar', token='TOKEN')
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

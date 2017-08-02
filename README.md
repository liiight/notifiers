# Notifiers
Generic way to use notification services

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

- Many more notifiers
- CLI
- Environment variable support
- Docs

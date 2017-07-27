# Notifiers
Generic way to use notification services

From python:
```python
import notifiers

pushover = notifiers.get_notifer('pushover')
pushover.notify(title='Foo', message='Bar', token='TOKEN')
```

From CLI: (gets token from environment variable, uses a default title. All can be overridden):
```bash
less file.txt | notify pushover 
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
pushover = notifiers.providers.Pushover
```

Send a notification:
```python
resp = pushover.notify(token='TOKEN', title='Foo', message='Bar')
```

Get notifier metadata:
```text
print(pushover.metadata)

{
    "url": "http://..."
    "description": "A Great notifier!"
    ..
}

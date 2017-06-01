# Notifiers
Generic way to use notification services

From python:
```python
pushover = notifiers.get_notifer('pushover)
pushover = pushover(token='TOKEN')
pushover.notify(title='Foo', message='Bar')
```

From CLI: (gets token from environment variable, uses a default title. All can be overriden):
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
pushover = notifiers.get_notifer('pushover')(token='TOKEN')
```
Or:
```python
pushover = notifiers.providers.Pushover(token='TOKEN')
```

Send a notification:
```python
resp = pushover.notify(title='Foo', message='Bar')
```

Get notifier metadata:
```python
print(pushover.metadata)

{
    "url": "http://..."
    "description": "A Great notifier!"
    ..
}

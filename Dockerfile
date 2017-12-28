FROM python:alpine3.6

RUN pip install notifiers

ENTRYPOINT ["notifiers"]
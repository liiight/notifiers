FROM python:alpine3.6

ADD . /notifiers
WORKDIR /notifiers

RUN pip install --upgrade pip setuptools
RUN pip install -e .
RUN pip install -r requirements.txt

ENTRYPOINT ["notifiers"]
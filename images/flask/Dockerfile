FROM python:3.11-rc-alpine

RUN pip install --upgrade pip

RUN apk add curl gcc bind-tools bind-dnssec-tools
RUN apk add --update --no-cache --virtual .tmp-build-deps \
    gcc libc-dev linux-headers postgresql-dev \
    && apk add libffi-dev build-base alpine-sdk

RUN adduser -D nonroot
RUN mkdir /home/app/ && chown -R nonroot:nonroot /home/app
RUN mkdir -p /var/log/flask-app && touch /var/log/flask-app/flask-app.err.log && touch /var/log/flask-app/flask-app.out.log
RUN chown -R nonroot:nonroot /var/log/flask-app
WORKDIR /home/app
COPY ./requirements.txt requirements.txt

ENV VIRTUAL_ENV=/home/app/venv

RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN export FLASK_APP=main.py

RUN pip install -r requirements.txt

COPY ./app /opt/app
RUN chown -R nonroot:nonroot /opt/app
USER nonroot


WORKDIR /opt/app
EXPOSE 8000

CMD ["gunicorn", "-w", "8", "main:app", "-b", "0.0.0.0:8000"]

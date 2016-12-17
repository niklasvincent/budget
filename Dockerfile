FROM alpine:3.4

RUN apk add --no-cache python && \
    python -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip install --upgrade pip setuptools supervisor && \
    rm -r /root/.cache

RUN mkdir /data
RUN mkdir /app

ADD sync.py /app
ADD web.py /app
ADD static /app/static
ADD budget /app/budget
ADD requirements.txt /app

COPY supervisord.conf /app/supervisord.conf

RUN pip install -r /app/requirements.txt

WORKDIR /data

EXPOSE 5000
CMD ["/usr/bin/supervisord", "-c", "/app/supervisord.conf"]

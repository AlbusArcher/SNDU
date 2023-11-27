FROM alpine:3.18

RUN apk update
RUN apk add python3 py3-pip
RUN pip3 install requests xmltodict

RUN mkdir /workdir
COPY main.py /workdir/main.py

ENTRYPOINT ["python3", "/workdir/main.py"]


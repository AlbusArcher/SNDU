FROM alpine:3.18

RUN apk update
RUN apk add python3 py3-pip tzdata
RUN pip3 install requests xmltodict

RUN apk cache clean
RUN pip3 cache purge
RUN ln -s /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

RUN mkdir /workdir
COPY main.py /workdir/main.py

WORKDIR /workdir
ENTRYPOINT ["python3", "main.py"]


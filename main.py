import os
import sys
import time
import logging
import datetime
import requests
import xmltodict
import logging.config


Env_API_KEY = os.getenv('API_KEY')
Env_HOST_NAME = os.getenv('HOST_NAME', '')
Env_DOMAIN_NAME = os.getenv('DOMAIN_NAME')
Env_CHECK_INTERVAL = os.getenv('CHECK_INTERVAL')
Env_IP_ECHO_SERVER = os.getenv('IP_ECHO_SERVER', 'https://ipecho.net/plain')
HOST_DOMAIN_TARGET = Env_HOST_NAME + '.' + Env_DOMAIN_NAME if len(Env_HOST_NAME) > 0 else Env_DOMAIN_NAME

URL_LIST_RECORD = 'https://www.namesilo.com/api/dnsListRecords?version=1&type=xml&key={key}&domain={domain}'
URL_ADD_RECORD = 'https://www.namesilo.com/api/dnsAddRecord?version=1&type=xml&key={key}&domain={domain}&rrtype=A&rrhost={host}&rrvalue={ip}&rrttl=7207'
URL_UPDATE_RECORD = 'https://www.namesilo.com/api/dnsUpdateRecord?version=1&type=xml&key={key}&domain={domain}&rrid={rid}&rrhost={host}&rrvalue={ip}&rrttl=7207'


def get_record() -> (bool, str, str):
    ret, rid, rip = False, str(), str()
    try:
        resp = requests.get(URL_LIST_RECORD.format(key=Env_API_KEY, domain=Env_DOMAIN_NAME))
        if resp.status_code == 200:
            dat = xmltodict.parse(resp.content)
            reply = dat['namesilo']['reply']
            if reply['detail'] == 'success':
                ret = True
                if isinstance(reply['resource_record'], dict):
                    item = reply['resource_record']
                    if item['type'] == 'A' and item['host'] == HOST_DOMAIN_TARGET:
                        rid, rip = item['record_id'], item['value']
                elif isinstance(reply['resource_record'], list):
                    for item in reply['resource_record']:
                        if item['type'] == 'A' and item['host'] == HOST_DOMAIN_TARGET:
                            rid, rip = item['record_id'], item['value']
    except Exception as e:
        logging.error('Get {} record info fail! Reason: {}'.format(HOST_DOMAIN_TARGET, e))
    return ret, rid, rip


def add_record(ip) -> str:
    rid = str()
    try:
        resp = requests.get(
            URL_ADD_RECORD.format(key=Env_API_KEY, domain=Env_DOMAIN_NAME,
                                  host=Env_HOST_NAME, ip=ip))
        if resp.status_code == 200:
            dat = xmltodict.parse(resp.content)
            reply = dat['namesilo']['reply']
            if reply['detail'] == 'success':
                rid = reply['record_id']
    except Exception as e:
        logging.error('Add {}:{} record info fail! Reason: {}'.format(HOST_DOMAIN_TARGET, ip, e))
    return rid


def update_record(rid, ip) -> bool:
    ret = False
    try:
        resp = requests.get(
            URL_UPDATE_RECORD.format(key=Env_API_KEY, domain=Env_DOMAIN_NAME,
                                     rid=rid, host=Env_HOST_NAME, ip=ip))
        if resp.status_code == 200:
            dat = xmltodict.parse(resp.content)
            reply = dat['namesilo']['reply']
            if reply['detail'] == 'success':
                ret = True
    except Exception as e:
        logging.error('Update {}:{} record info fail! Reason: {}'.format(HOST_DOMAIN_TARGET, ip, e))
    return ret


def get_wan_ip() -> str:
    wip = str()
    try:
        resp = requests.get(Env_IP_ECHO_SERVER)
        if resp.status_code == 200:
            wip = resp.content.decode('utf8')
    except Exception as e:
        logging.error('Get Wan IP fail! Reason: {}'.format(e))
    return wip


def log_init():
    LOG_CONFIG = {
        'version': 1,
        'formatters': {
            'default': {
                'format': '%(asctime)s - %(levelname)s : %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            }
        },
        'handlers': {
            'file': {
                'level': 'INFO',
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'default',
                'filename': '/workdir/main.log',
                'maxBytes': 536870912,
                'backupCount': 10
            }
        },
        'loggers': {
            'root': {
                'level': 'INFO',
                'handlers': ['file']
            }
        },
        'disable_existing_loggers': False
    }
    logging.config.dictConfig(LOG_CONFIG)


if __name__ == '__main__':
    # log init
    log_init()
    
    # check env
    if Env_API_KEY is None or len(Env_API_KEY) == 0:
        sys.exit('Environment variable: API_KEY is Invalid!')

    if Env_DOMAIN_NAME is None or len(Env_DOMAIN_NAME) == 0:
        sys.exit('Environment variable: DOMAIN_NAME is Invalid!')

    interval_sec = 300
    if Env_CHECK_INTERVAL is not None:
        try:
            interval_sec = int(Env_CHECK_INTERVAL)
        except:
            sys.exit('Environment variable: CHECK_INTERVAL is Invalid!')

    while True:
        wan_ip = get_wan_ip()
        if len(wan_ip) > 0:
            result, record_id, record_ip = get_record()
            if result is True:
                if len(record_id) > 0:
                    if wan_ip != record_ip:
                        if update_record(record_id, wan_ip):
                            logging.info('UPDATE {}:{} -> {}'.format(HOST_DOMAIN_TARGET, record_ip, wan_ip))
                else:
                    record_id = add_record(wan_ip)
                    if len(record_id) > 0:
                        logging.info('ADD {}:{}'.format(HOST_DOMAIN_TARGET, wan_ip))
        time.sleep(interval_sec)


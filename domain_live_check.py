#! /usr/bin env python3
# -*- coding:utf-8 -*-


import requests
from threading import Thread
from queue import Queue
import socket
import os
import http.client
from functools import wraps
import datetime
import sys


concurrent = 10
q = Queue(concurrent * 2)

Headers = {
    "Upgrade-Insecure-Requests": '1',
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0",
    "Connection": "close"
    # "Connection": "keep-alive"
}

# get script path and switch path
path = os.path.split(os.path.realpath(__file__))[0] + '/'
os.chdir(path)


domain_survey = []


def timethis(func):
    """
    Decorator that reports the execution time
    """
    @wraps(func)
    def warpper(*args, **kwargs):
        start = datetime.datetime.now()
        result = func(*args, **kwargs)
        end = datetime.datetime.now()
        print(func.__name__, end - start)
        return result
    return warpper


def get_ip(domain):
    try:
        ip = socket.gethostbyname(domain)
        return ip
    except Exception as err:
        return None


# transfer doamin -> url
def get_url(host):
    conn = http.client.HTTPConnection(host, timeout=3)
    try:
        conn.request("HEAD", "")
    except Exception as err:
        # print(("1", host, str(err)))
        host = "www." + host
        conn = http.client.HTTPConnection(host, timeout=3)
        try:
            conn.request("HEAD", "")
        except Exception as err:
            pass
            # print(("2", host, str(err)))

    try:
        conn.getresponse()
        ret = "http://" + host
    except Exception as err:
        # print(("3", host, str(err)))
        ret = "https://" + host
    return ret


def url_scanner(url):
    try:
        res = requests.head(url, timeout=3, headers=Headers)
        if res.status_code == 200:
            return True
        else:
            return False
    except Exception as err:
        print(str(err))
        return False


def domain_scanner(domain):
    ip = get_ip(domain)
    if ip:
        url = get_url(domain)
        return url_scanner(url)
    else:
        return False


def worker():
    global domain_survey
    try:
        while True:
            domain = q.get()
            domain_check = domain_scanner(domain)
            print(domain, "\t\t", domain_check)
            domain_survey.append([domain, str(domain_check)])
            q.task_done()
    except Exception as err:
        print(err)


@timethis
def main():
    try:
        path = sys.argv[1]
    except Exception as err:
        print("\nPlease input file name!")
        sys.exit(0)

    for i in range(concurrent):
        t = Thread(target=worker)
        t.daemon = True
        t.start()
    
    try:
        with open(path, "r", encoding="utf-8") as fr:
            for line in fr:
                item = line.strip()
                if item:
                    q.put(item)
        q.join()
    except Exception as err:
        print(err)
    
    if q.empty():
        with open("result.csv", "w", encoding="utf-8") as fw:
            for line in domain_survey:
                fw.write(",".join(line) + "\n")


if __name__ == "__main__":
    main()
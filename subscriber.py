import sys
import time

from random import randint
import json
import os

import zmq

def nosub(nrosala):
    ctx = zmq.Context.instance()
    porta = 5546+nrosala
    subscriber = ctx.socket(zmq.SUB)
    url = "tcp://localhost:"+str(porta)
    subscriber.connect(url)

    subscription = b"%03d" % nrosala
    subscriber.setsockopt(zmq.SUBSCRIBE, subscription)

    while True:
        topic, data = subscriber.recv_multipart()
        assert topic == subscription
        print(data)

def main(url=None):
    nrosala=1
    for i in range(10):
        pid = os.fork()
        if pid == 0:
            nosub(nrosala)
            os._exit(0)
        else:
            nrosala+=1

if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else None)
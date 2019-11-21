import zmq
import time 
import random
import math 
import json
import os

def truncate(number, digits) -> float:
    stepper = pow(10.0, digits)
    return math.trunc(stepper * number) / stepper

def nocoletor(nrosala):
    ctx = zmq.Context.instance()
    publisher = ctx.socket(zmq.PUB)
    publisher.connect("tcp://127.0.0.1:5557")
    # Ensure subscriber connection has time to complete
    time.sleep(1)
    # Temperatura inicial
    temperatura= random.randint(200,300) /10

    while True:
        # Simulação de variação da temperatura, sendo possível variar de -0.5 a 0.5º a cada segundo
        rand = random.randint(-5,6)
        rand= rand/20
        temperatura+=rand
        temperatura = truncate(temperatura,1)
        json_string = '{"temperatura":'+str(temperatura)+', "sala":'+str(nrosala)+'}'
        json_decodificado = json.loads(json_string)
        publisher.send_multipart([
                b"%03d" % nrosala,
                json_string.encode(),
            ])
        time.sleep(1)

nrosala=1
for i in range(10):
    pid = os.fork()
    if pid == 0:
        random.seed()
        nocoletor(nrosala)
        os._exit(0)
    else:
        nrosala+=1
os.wait()
    
    
    
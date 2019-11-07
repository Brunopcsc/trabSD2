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
    context = zmq.Context()
    #  Socket to talk to server
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5555")
    # Temperatura inicial
    temperatura= random.randint(20,30)
    print(nrosala)
    print(temperatura)

    while True:
        # Simulação de variação da temperatura, sendo possível variar de -0.5 a 0.5º a cada segundo
        rand = random.randint(-5,5)
        rand= rand/10
        temperatura+=rand
        temperatura = truncate(temperatura,1)
        json_string = '{"temperatura":'+str(temperatura)+', "sala":'+str(nrosala)+'}'
        json_decodificado = json.loads(json_string)
        socket.send(json_string.encode())
        message = socket.recv()
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
    
    
    
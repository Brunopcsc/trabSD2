import zmq
import time 
import random
import math 
import json
import os
import sys
from datetime import datetime

# Função para truncar um número
def truncate(number, digits) -> float:
    stepper = pow(10.0, digits)
    return math.trunc(stepper * number) / stepper

# Função que será executada por cada processo fork simulando a variação de temperatura em salas
def nocoletor(nrosala,url):
    ctx = zmq.Context.instance()
    publisher = ctx.socket(zmq.PUB)
    if url:
        publisher.connect(url)
    else:
        publisher.connect("tcp://localhost:5557")
    # Ensure subscriber connection has time to complete
    time.sleep(1)
    # Temperatura inicial randômica
    temperatura = random.randint(200,300) /10

    while True:
        # Simulação de variação da temperatura, sendo possível variar de -0.3 a 0.3º a cada segundo
        rand = random.randint(-3,3)
        rand = rand/10
        temperatura += rand
        temperatura = truncate(temperatura,1)
        now = datetime.now()
        now = str(now)
        now=now.split(' ')
        now2 = now[1].split('.')
        now3 = now2[0]
        # Empacota os dados em uma string JSON
        json_string = '{ "temperatura":"'+str(temperatura)+'", "timestamp":"'+str(now3)+'"}'
        # Envia o pacote para o broker, sendo o tópico o número da sala
        publisher.send_multipart([
                b"%03d" % nrosala,
                json_string.encode(),
            ])
        time.sleep(1)

def main(url=None):
    nrosala=1
    # Cria 8 ṕublishers com o Fork
    for i in range(8):
        pid = os.fork()
        if pid == 0:
            random.seed()
            nocoletor(nrosala,url)
            os._exit(0)
        else:
            nrosala+=1
    os.wait()
    
if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else None)    
    
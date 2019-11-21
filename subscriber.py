import sys
import time
import matplotlib.pyplot as plt
from random import randint
import json
import os
import math
from multiprocessing import Queue
import zmq

# Função para truncar um número
def truncate(number, digits) -> float:
    stepper = pow(10.0, digits)
    return math.trunc(stepper * number) / stepper

# Função executada por cada nó subscriber responsável por realizar a leitura de cada mensagem
# referente ao seu tópico inscrito
def nosub(nrosala,url):
    ctx = zmq.Context.instance()
    subscriber = ctx.socket(zmq.SUB)
    if url is None:
        url = "tcp://localhost:5558"
    subscriber.connect(url)
    # Indíce usado para inserir o log de temperaturas em um dicionário. 
    indice=0
    # Nome do tópico inscrito, sendo no caso apenas o número da sala
    subscription = b"%03d" % nrosala;
    subscriber.setsockopt(zmq.SUBSCRIBE, subscription)
    # Loop para ler sem parar as mensagens recebidas
    while True:
        topic, data = subscriber.recv_multipart()
        data = data.decode()
        assert topic == subscription
        # Desempacota o JSON recebido
        json_decodificado = json.loads(data)
        # Cria um log para enviar ao processo pai cada mensagem recebida
        log = {"Indice":indice,"Sala":nrosala,"TimeStamp": json_decodificado['timestamp'],"Temperatura":json_decodificado['temperatura']}
        # Envia o log para uma fila de comunicação entre processos
        q.put(log)
        indice+=1


q = Queue()
def main(url=None):
    indice = 0
    # Dicionário para armazenar os logs de temperaturas de todas salas
    temp = {}
    nrosala=1
    # Cria uma fila para realizar troca de mensanges entre processos
    # Cria os subscribers, cada um inscrito no tópico referente a uma sala 
    for i in range(8):
        pid = os.fork()
        if pid == 0:
            nosub(nrosala,url)
            os._exit(0)
        else:
            nrosala+=1
    # Dorme por 11 segundos para ser possível gerar um gráfico com as últimas 10 leituras de temperatura
    time.sleep(11)
    while True:
        # Lê da fila todos os logs e armazena no dicionário
        while not q.empty():
            log = q.get()
            ind = log["Indice"]
            sala = log["Sala"]
            timestamp = log["TimeStamp"]
            temperatura = log["Temperatura"]
            log = {"Sala":sala,"TimeStamp": timestamp,"Temperatura":temperatura}
            if not temp.get(ind):
                temp[ind]=[]
            temp[ind].append(log)
            if ind>indice:
                indice=ind

        media={}
        tempo = []
        # Plota no gráfico a variação de temperatura nos últimos 10 segundos de todas as salas
        for j in range(8):
            valores = []
            for i in range(10):
                for log in temp[indice-10+i]:
                    if int(log["Sala"]) == int(j+1):
                        valores.append(float(log['Temperatura']))
                        if j==0:
                            tempo.append(log['TimeStamp'])
            xn = range(10)
            lbl = "Sala " + str(j+1)
            media[j+1] = sum(valores)/len(valores)
            plt.plot(xn,valores,label=lbl)
            valores = []
        plt.xticks(xn,tempo)
        plt.title("Variação de temperatura nas salas")

        plt.grid(True)

        plt.xlabel("Horário")
        plt.ylabel("Temperatura")
        plt.legend()
        plt.ion()
        plt.show()
        plt.draw()
        plt.pause(0.001)
        plt.clf()
        for i in range(8):        
            med = truncate(media[i+1],2)
            print("Temperatura média nos últimos 10 segundos na sala "+str(i+1)+": "+str(med))

if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else None)



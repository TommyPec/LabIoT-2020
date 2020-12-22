########## Importazione moduli ##########
import paho.mqtt.client as mqtt
import socket
import threading
import configparser
import logging


########## Parametri ##########
config = configparser.ConfigParser()
config.read('config.ini')
port = config['RASPBERRY']['port']
addr = config['RASPBERRY']['address']
gateway = (addr, int(port))
addr_broker = config['mqtt_broker']['address']
port_broker = config['mqtt_broker']['port']
topic = "test/topic"


########## Definizione coda FIFO ##########
class Queue:
    def __init__(self):
        self.items = []
        self.elem = 0
        self.head = None

    def notEmpty(self):
        return self.elem != 0

    def inQueue(self, item):
        self.items.insert(0,item)
        if(self.elem == 0):
            self.head = item
        self.elem += 1

    def outQueue(self):
        if(self.elem == 1):
            self.head = None
        self.elem -= 1
        return self.items.pop()


########## on_connect() ##########
def on_connect(pubsub, userdata, flags, rc):
    if(rc != 0):
        logging.warning(f"Connessione al Broker con indirizzo IPv4 {addr_broker} fallita: codice [{rc}].\n")
    else:
        print(f"Connessione al Broker con indirizzo IPv4 {addr_broker} riuscita.\n")
    try:
        result, mid = pubsub.subscribe(topic)
        if(result != 0):
            logging.warning(f"Iscrizione al topic {topic} fallita: codice [{result}].\n")
        else:
            print(f"Iscrizione al topic {topic} riuscita.\n")
    except Exception as err:
        logging.error(f"Errore in iscrizione al topic {topic}:\n{err}\n")


########## on_disconnect() ##########
def on_disconnect(pubsub, userdata, rc):
    if(rc != 0):
        logging.warning(f"Disconnessione inaspettata dal Broker con indirizzo IPv4 {addr_broker}: codice [{rc}].\n")
    else:
        print(f"Disconnessione dal Broker con indirizzo IPv4 {addr_broker}.\n")
        

########## on_message() ##########
def on_message(pubsub, userdata, msg):
    data = msg.payload.decode('utf-8')
    print("### [" + msg.topic + "] ###\n" + data + "\n")


########## MQTT Publishing ##########
def queue2broker(pubsub, q):
    pubsub.loop_start()
    while True:
        if(q.notEmpty()):
            data = q.outQueue()
            pubsub.publish(topic, data)
    pubsub.loop_stop()


########## Ricezione da Client UDP ##########
def client2queue(s, q):
    while True:
        msg, client = s.recvfrom(4096)
        data = f"Client: {client}" + "\n" + msg.decode()
        q.inQueue(data)


########## Creazione Gateway ##########
def initialize(gateway):
    # Server UDP
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    except socket.error as err:
        try:
            s.close()
        except Exception:
            pass
        raise SystemError(f"Errore in creazione socket:\n{err}\n")
    try:
        s.bind(gateway)
    except socket.error as err:
        try:
            s.close()
        except Exception:
            pass
        raise SystemError(f"Errore in bind socket:\n{err}\n")
    print("Server UDP inizializzato. In ascolto...\n")
    # Client MQTT
    pubsub = mqtt.Client(client_id = "", clean_session = True, userdata = None)
    pubsub.on_connect = on_connect
    pubsub.on_disconnect = on_disconnect
    pubsub.on_message = on_message
    try:
        pubsub.connect(addr_broker, int(port_broker), 60)
    except Exception as err:
        logging.error(f"Errore in connessione al Broker con indirizzo IPv4 {addr_broker}:\n{err}\n")
    # Avvio Gateway
    q = Queue()
    thread_out = threading.Thread(target = queue2broker, args = (pubsub, q))
    thread_in = threading.Thread(target = client2queue, args = (s, q))
    thread_out.start()
    thread_in.start()


########## Programma ##########
if __name__ == '__main__':
    initialize(gateway)

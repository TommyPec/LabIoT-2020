########## Importazione moduli ##########
import paho.mqtt.client as mqtt
import socket
import threading


########## Parametri ##########
port = 20000
addr = "192.168.1.57"  # Cambiare con l'indirizzo IPv4 del proprio gateway (RB/PC)
gateway = (addr, port)
addr_broker = "10.108.230.1"
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
    print(f"Risultato connessione al broker con indirizzo IPv4 {addr_broker} (0 -> successo): [{rc}]\n")
    pubsub.subscribe(topic)
    print(f"Iscritto al topic: {topic}\n")


########## on_disconnect() ##########
def on_disconnect(pubsub, userdata, rc):
    if(rc != 0):
        print(f"Disconnessione inaspettata: codice [{rc}].\n")
    else:
        print(f"Disconnessione dal broker con indirizzo IPv4 {addr_broker}.\n")


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
        s.bind(gateway)
        print("Server UDP inizializzato. In ascolto...\n")
    except socket.error as err:
        print(f"Qualcosa è andato storto...\n{err}.\n")
        print("Sto tentando di reinizializzare il Server UDP...\n")
        initialize(gateway)
    # Publisher MQTT
    pubsub = mqtt.Client(client_id = "", clean_session = True, userdata = None)
    pubsub.on_connect = on_connect
    pubsub.on_disconnect = on_disconnect
    pubsub.on_message = on_message
    pubsub.connect(addr_broker, 1883, 60)
    # Avvio Gateway
    q = Queue()
    thread_out = threading.Thread(target = queue2broker, args = (pubsub, q))
    thread_in = threading.Thread(target = client2queue, args = (s, q))
    thread_out.start()
    thread_in.start()


########## Programma ##########
if __name__ == '__main__':
    initialize(gateway)

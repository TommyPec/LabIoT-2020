########## Importazione moduli ##########
import paho.mqtt.client as mqtt
import socket
import threading


########## Parametri ##########
port = 20000
addr = "192.168.1.57" # Cambiare con l'indirizzo IPv4 del proprio gateway (RB/PC)
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
def on_connect(pub, userdata, flags, rc):
    print(f"Risultato connessione al broker con indirizzo IPv4 {addr_broker} (0 -> successo): [{rc}]\n")

def on_disconnect(pub, userdata, rc):
    if(rc != 0):
        print(f"Disconnessione inaspettata: codice [{rc}].\n")
    else:
        print(f"Disconnessione dal broker con indirizzo IPv4 {addr_broker}.\n")


########## MQTT Publishing ##########
def queue2broker(pub, q):
    pub.loop_start()
    while True:
        if(q.notEmpty()):
            data = q.outQueue()
            pub.publish(topic, data)
    pub.loop_stop()


########## Ricezione da Client TCP ##########
def client2queue(s_client, addr_client, q):
    while True:
        msg = s_client.recv(4096)
        if(msg == b''):
            print(f"Il Client {addr_client} si è disconnesso.\nChiudo il socket: {s_client}.\n")
            s_client.close()
            break
        data = f"Client: {addr_client}" + "\n" + msg.decode()
        q.inQueue(data)


########## Accettazione Client TCP ##########
def gateway_threads(s, pub, q):
    thread1 = threading.Thread(target = queue2broker, args = (pub, q))
    thread1.start()
    while True:
        s_client, addr_client = s.accept()
        print(f"Connessione con Client TCP {addr_client} stabilita.\n")
        thread2 = threading.Thread(target = client2queue, args = (s_client, addr_client, q))
        thread2.start()


########## Creazione Gateway ##########
def initialize(gateway):
    # Server TCP
    try:
        s = socket.socket()
        s.bind(gateway)
        s.listen(0)
        print("Server TCP inizializzato. In ascolto...\n")
    except socket.error as err:
        print(f"Qualcosa è andato storto...\n{err}.\n")
        print("Sto tentando di reinizializzare il Server TCP...\n")
        initialize(gateway)
    # Publisher MQTT
    pub = mqtt.Client(client_id="", clean_session=True, userdata=None)
    pub.on_connect = on_connect
    pub.on_disconnect = on_disconnect
    pub.connect(addr_broker, 1883, 10)
    # Avvio Gateway
    q = Queue()
    gateway_threads(s, pub, q)


########## Programma ##########
if __name__ == '__main__':
    initialize(gateway)

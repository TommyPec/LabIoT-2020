########## Importazione moduli ##########
import paho.mqtt.client as mqtt
import socket
import threading
import configparser
import logging


########## Parametri ##########
config = configparser.ConfigParser()
config.read('config_Bluetooth.ini')
port = config['RASPBERRY']['port']
addr = config['RASPBERRY']['MAC_address']
gateway = (addr, int(port))
addr_target = config['ESP32']['MAC_address']
addr_broker = config['mqtt_broker']['IPv4_address']
port_broker = config['mqtt_broker']['port']
topic = "test/topic"


########## Definizione coda FIFO ##########
class Queue:
    def __init__(self):
        self.items = []
        self.elem = 0
        self.head = None

    def elemCount(self):
        return self.elem

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
        

########## on_message() ##########  MODIFICARE IN BASE AL SUCCESSIVO UTILIZZO DEI CAMPIONI OTTENUTI
def on_message(pubsub, userdata, msg):
    data = msg.payload.decode('utf-8')
    print("### [" + msg.topic + "] ###\n" + data + "\n")


########## MQTT Publishing ##########
def queue2broker(pubsub, q):
    pubsub.loop_start()
    # MODIFICARE IN BASE AL PROCESSING DA FARE DA QUI
    while True:
        if(q.elemCount != 0):
            data = q.outQueue()
            pubsub.publish(topic, data)
    # MODIFICARE IN BASE AL PROCESSING DA FARE FINO A QUI
    pubsub.loop_stop()


########## Connessione e ricezione da Client Bluetooth ##########
def client2queue(s, q):
    # Listening di potenziali Client
    try:
        s.listen(0)
    except socket.error as err:
        try:
            s.close()
        except Exception:
            pass
        raise SystemError(f"Errore in listen socket Bluetooth RFCOMM:\n{err}\n")
    print("Server Bluetooth RFCOMM in attesa del Client target {addr_target}.\n")
    # Ricerca del Client target e connessione
    while True:
        try:
            s_client, addr_client = s.accept()
        except socket.error as err:
            try:
                s.close()
            except Exception:
                pass
            raise SystemError(f"Errore nel tentativo di connessione al Client target {addr_target}:\n{err}\n")
        if(addr_client == addr_target)
            break;
        else
            s_client.close()
    print(f"Server Bluetooth RFCOMM connesso al Client target {addr_target}.\n")
    # Ricezione da Client target
    while True:
        msg = s_client.recv(4096)
        q.inQueue(msg.decode())


########## Creazione Gateway ##########
def initialize(gateway):
    # Server Bluetooth RFCOMM
    try:
        s = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
    except socket.error as err:
        try:
            s.close()
        except Exception:
            pass
        raise SystemError(f"Errore in creazione socket Bluetooth RFCOMM:\n{err}\n")
    try:
        s.bind(gateway)
    except socket.error as err:
        try:
            s.close()
        except Exception:
            pass
        raise SystemError(f"Errore in bind socket Bluetooth RFCOMM:\n{err}\n")
    print("Server Bluetooth RFCOMM inizializzato con successo.\n")
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

########## Importazione moduli ##########
import paho.mqtt.client as mqtt


########## Parametri ##########
addr_broker = "10.108.230.1"
topic = "test/topic"


########## on_connect() ##########
def on_connect(sub, userdata, flags, rc):
    print(f"Risultato connessione al broker con indirizzo IPv4 {addr_broker} (0 -> successo): [{rc}]\n")
    sub.subscribe(topic)
    print(f"Iscritto al topic: {topic}\n")


########## on_message() ##########
def on_message(sub, userdata, msg):
    data = msg.payload.decode('utf-8')
    print("### [" + msg.topic + "] ###\n" + data + "\n")


########## Creazione & Connessione MQTT Subscriber ##########
def new_subscriber():
    sub = mqtt.Client()
    sub.on_connect = on_connect
    sub.on_message = on_message
    sub.connect(addr_broker, 1883, 60)
    sub.loop_forever()
    
    
########## Programma ##########
if __name__ == '__main__':
    new_subscriber()

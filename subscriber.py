import paho.mqtt.client as mqtt

#The callback for when the client receives a CONNACK response from the server
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect the subscriptions will be renewd.
    client.subscribe("$SYS/#")

#The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

def new_client()
    client = mqtt.Client()
    client.on_connect = on_connect

    client.connect("mqtt.eclipse.org", 1883, 60)
    # Blocking call that process network traffic, dispatches callbacks and
    # handles reconnecting.
    # Other loop*() functions are available that give a threaded interface and a
    # manual interfacee.
    client.loop_forever()
    
    client.on_disconnect = on_disconnect
    client.on_publish = on_publish
    client.on_subscribe = on_subscribe
    client.on_message = on_message
topics=[("house/light/bulb1",0),("house/light/bulb2",1)]
topic_ack=[]
print("Connecting to broker ", broker)
try:
    client.connect(broker)          #connect to broker
except:
    print("can't connect")
    sys.exit(1)
client.loop_start()                 #start loop
while not client.connected_flag:    #wait in loop
    print("In wait loop")
    time.sleep(1)
####
print("subscribing "+str(topics))
for t in topics:
    try:
        r=client.subscribe(t)
        if r[0]==0:
            logging.info("subscribed to topic "+str(t[0])+" return code"+str(r))
            topic_ack.append([t[0],r[1],0) #keep track of subscription
        else:
            logging.info("error on subscribing "+str(r))
            client.loop_stop()      #stop loop
            sys.exit(1)
    except Exception as e:
        logging.info("error on subscribe"+str(e))
        client.loop_stop()          #stop loop
        sys.exit(1)
print("waiting for all subs")
while not check_subs():
    time.sleep(1)
###
msg="off"
print("Publishing topic= ",topics[0][0], "message= ",msg)
client.publish(topics[0][0],msg)
time.sleep(4)
client.loop_stop()                  #stop loop
client.disconnect()                 #disconnect

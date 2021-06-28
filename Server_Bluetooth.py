########## Importazione moduli ##########
import socket


########## Parametri ##########
port = 3
addr = "" # Inserire l'indirizzo MAC della scheda Bluetooth del RB
server = (addr, port)
addr_target = "" # Inserire l'indirizzo MAC della scheda Bluetooth del PC


########## Server Bluetooth ##########
def start(server):
    # Creazione socket d'ascolto
    s = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
    s.bind(gateway)
    print("Server Bluetooth RFCOMM inizializzato con successo.\n")
    s.listen(0)
    print("Server Bluetooth RFCOMM in attesa del Client target {addr_target}.\n")
    # Connessione al Client target
    while True:
        s_client, addr_client = s.accept()
        if(addr_client == addr_target)
            break;
        else
            s_client.close()
    print("Server Bluetooth RFCOMM connesso al Client target {addr_target}.\n")
    # Ricezione da Client target e print
    while True:
        msg = s_client.recv(4096)
        print("\n" + msg.decode() + "\n")


########## Programma ##########
if __name__ == '__main__':
    start(server)

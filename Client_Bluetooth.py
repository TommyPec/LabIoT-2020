########## Importazione moduli ##########
import socket
import sys


########## Parametri ##########
port = 3
addr_server = "" # Inserire l'indirizzo MAC della scheda Bluetooth del RB
server = (addr_server, port)


########## Gestione del Client Bluetooth ##########
def command_line(s):
    sensor_string = "(x,y,z)"
    while True:
        cmd = input("-> s = invia pacchetto al Server.\n-> q = chiudi la connessione.\n\t-> ")
        if cmd == "q":
            print("Sto chiudendo la connessione col Server...")
            s.close()
            print(f"Connessione col Server {addr_server} chiusa.\n")
            sys.exit()
        elif cmd == "s":
            s.send(sensor_string.encode())
            print("Inviato pacchetto al Server.\n")
        else:
            print("Il comando digitato è invalido.\n")


########## Creazione & Connessione Client Bluetooth ##########
def start_client(server):
    # Creazione socket
    s = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
    print("Client Bluetooth RFCOMM inizializzato con successo.\n")
    # Connessione al Server
    s.connect(server)
    print(f"Client Bluetooth RFCOMM connesso al Client target {addr_server}.\n")
    # Routine invio pacchetti
    command_line(s)
        

########## Programma ##########
if __name__ == '__main__':
    start_client(server)

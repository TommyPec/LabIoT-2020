########## Importazione moduli ##########
import socket
import sys


########## Parametri ##########
port = 20000
addr_server = "192.168.1.57" # Cambiare con l'indirizzo IPv4 del proprio gateway (RB/PC)
server = (addr_server, port)


########## Oggetto per il test ##########
sensor_string = '''{
  "measurement":
    {
      "temperature": "12.5 C",
      "umidity": "63 %"
    }
}'''


########## Gestione del Client TCP ##########
def client_send(s):
    while True:
        cmd = input("-> s = invia pacchetto al Server.\n-> q = chiudi la connessione.\n\t-> ")
        if cmd == "q":
            print("Sto chiudendo la connessione col Server...")
            s.close()
            print(f"Connessione col Server {server} chiusa.\n")
            sys.exit()
        elif cmd == "s":
            s.send(sensor_string.encode())
            print("Inviato pacchetto al Server.\n")
        else:
            print("Il comando digitato è invalido.\n")


########## Creazione & Connessione Client TCP ##########
def new_client_connect(server):
    try:
        s = socket.socket()
        s.connect(server)
        print(f"Connessessione al Server {addr_server} effettuata.\n")
    except socket.error as err:
        print(f"Qualcosa è andato storto, sto uscendo...\n{err}.\n")
        sys.exit()
    client_send(s)
        

########## Programma ##########
if __name__ == '__main__':
    new_client_connect(server)

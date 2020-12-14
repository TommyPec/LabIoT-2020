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
def client_send(s, server):
    while True:
        cmd = input("-> s = invia pacchetto al Server.\n-> q = chiudi il socket.\n\t-> ")
        if cmd == "q":
            print("Sto chiudendo il socket...")
            s.close()
            print(f"Socket chiuso.\n")
            sys.exit()
        elif cmd == "s":
            s.sendto(sensor_string.encode(), server)
            print("Inviato pacchetto al Server.\n")
        else:
            print("Il comando digitato è invalido.\n")


########## Creazione & Connessione Client UDP ##########
def new_client_connect(server):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print(f"Connessessione al Server {addr_server} effettuata.\n")
    except socket.error as err:
        print(f"Qualcosa è andato storto, sto uscendo...\n{err}.\n")
        sys.exit()
    client_send(s, server)
        

########## Programma ##########
if __name__ == '__main__':
    new_client_connect(server)

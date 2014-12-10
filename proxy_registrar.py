#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
# Practica 4 Javier Fernandez Marugan  PTAVI
"""
Clase (y programa principal) para un servidor Register SIP
"""
import SocketServer
import sys
import time


class SIPRegisterHandler(SocketServer.DatagramRequestHandler):
    """
    Servidor
    """
    def register2file(self, Dic_clients):
        """
        Método reescribir el fichero con los datos del diccionario,
        revisando previamente si expiró el tiempo de alguno de los clientes
        """
        fich = open("registered.txt", "w")
        fich.write("User" + "\t" + "IP" + "\t" + "Expires" + "\n")
        now = time.time()
        keys = Dic_clients.keys()
        for element in keys:
            if Dic_clients[element][1] > now:
                addr = Dic_clients[element][0]
                exp = Dic_clients[element][1]
                expire = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(exp))
                fich.write(element + "\t" + str(addr) + "\t" + expire + "\n")
            else:
                address = Dic_clients[element][0]
                del Dic_clients[element]
                print "Expiró el tiempo del cliente: (" + element,
                print " , " + address + ")"
        fich.close()

    def handle(self):
        """
        Método para manejar las peticiones de los clientes y
        actuar en funcion de su contenido
        """
        # Escribe dirección y puerto del cliente (de tupla client_address)
        self.wfile.write("SIP/2.0 200 OK" + '\r\n')
        while 1:
            # Leemos línea a línea lo que nos envía el cliente y
            # lo separamos por espacios
            line = self.rfile.read()
            lista = line.split(" ")

            if line != "":
                # Construimos el cliente y lo añadimos al diccionario
                # (reemplazamos expire si ya existía)
                if lista[0] == "REGISTER":
                    now = time.time()
                    Nick = lista[1].split(":")
                    expire = time.time() + int(lista[3])
                    self.register2file(Dic_clients)
                    Dic_clients[Nick[1]] = (self.client_address[0], expire)
                    # Si expire = 0 damos de baja al cliente y actualizamos
                    # el diccionario de clientes y con ello el fichero
                    if lista[3] == '0':
                        print "Cliente dado de baja: (",
                        print str(self.client_address[0]),
                        print " , " + str(self.client_address[1]) + ")"
                        del Dic_clients[Nick[1]]
                        self.wfile.write("SIP/2.0 200 OK" + '\r\n')
                        self.register2file(Dic_clients)

                    # Si el expires es mayor que 0 imprimimos al cliente y su
                    # mensaje. Imprimimos el diccionario en el fichero
                    else:
                        print "Cliente Registrado: (",
                        print str(self.client_address[0]),
                        print " , " + str(self.client_address[1]) + ")"
                        print 'El cliente nos manda: ' + line
                        self.wfile.write("SIP/2.0 200 OK" + '\r\n')
                        self.register2file(Dic_clients)
                else:
                    self.wfile.write("SIP/2.0 400 BAD REQUEST" + '\r\n')
            if not line:
                break

if __name__ == "__main__":
    # Creamos un diccionario de clientes vacio, servidor de eco y escuchamos
    Dic_clients = {}
    PORT = int(sys.argv[1])
    serv = SocketServer.UDPServer(("", PORT), SIPRegisterHandler)
    print "Lanzando servidor UDP de eco..."
    serv.serve_forever()

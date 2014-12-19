#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
# Practica 4 Javier Fernandez Marugan  PTAVI
"""
Clase (y programa principal) para un servidor Register SIP
"""
import SocketServer
import sys
import os
import time
from xml.sax import make_parser
from xml.sax.handler import ContentHandler


class XMLHandler_PROXY(ContentHandler):

    def __init__(self):

        self.labels={"server_name":"", "server_ip":"",
            "server_puerto":"","database_path":"","database_passwdpath":"",
            "log_path":""}   

        self.atributes=["name", "ip", "puerto", "path", "passwdpath"]

    def startElement(self, name, attrs):

        dic={}
        label = name[0:3]
        all_labels = self.labels.keys()
        key_wanted = ""
        for count in range(len(all_labels)):    #quiero que count sea número
            if label == all_labels[count][0:3]:
                key_wanted = all_labels[count].split("_")[0]
                #print "@@@@@@@@@@@@@@@@@@@@@@@" + key_wanted
                break

        for atribute in self.atributes:
            #print "###################" + atribute
            label = key_wanted + "_" + atribute
            if label in self.labels:
                self.labels[label] = attrs.get(atribute, "")
                #print "Encuentro un atributo ~~~~~~~~~~~~~~" + atribute
                #print "Guardo de el ===========" + self.labels[label]
        dic_atributes = self.labels

    def get_tags(self):
        return self.labels.keys()
        
    def get_labels(self):
        return self.labels


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

    try:
        FICH = sys.argv[1]
        if not os.access(sys.argv[1], os.F_OK):
            print "Usage: the file doesn't exist"
            sys.exit()
    except ValueError:
        print "Usage: python proxy_registrar.py config"

    parser = make_parser()
    Handler = XMLHandler_PROXY()
    parser.setContentHandler(Handler)
    parser.parse(open(FICH))
    dic_labels = Handler.get_labels()
    print dic_labels
    IP = dic_labels["server_ip"]
    PORT = int(dic_labels["server_puerto"])
    NAME = dic_labels["server_name"]
    if IP == "" or PORT == "" or NAME == "":
        print "Usage Error: xml file need too much proxy values"
        sys.exit()
    phrase = "\r\nStarting Server Proxy/Registrar " + NAME + " listening at "
    print phrase + str(IP) + " port " + str(PORT)
    # Creamos servidor de SIP y escuchamos
    #SERVER Y PORT ESTAN EN EL FICHERO XML
    serv = SocketServer.UDPServer((IP, PORT), SIPRegisterHandler)
    serv.serve_forever()



"""

if __name__ == "__main__":
    # Creamos un diccionario de clientes vacio, servidor de eco y escuchamos
    Dic_clients = {}
    PORT = int(sys.argv[1])
    serv = SocketServer.UDPServer(("", PORT), SIPRegisterHandler)
    print "Lanzando servidor UDP de eco..."
    serv.serve_forever()
    
"""

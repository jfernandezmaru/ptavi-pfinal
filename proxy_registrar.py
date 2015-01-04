#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
# Practica 4 Javier Fernandez Marugan  PTAVI
"""
Clase (y programa principal) para un servidor Register SIP
"""
import SocketServer
import socket
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
        for count in range(len(all_labels)):
            if label == all_labels[count][0:3]:
                key_wanted = all_labels[count].split("_")[0]
                break

        for atribute in self.atributes:
            label = key_wanted + "_" + atribute
            if label in self.labels:
                self.labels[label] = attrs.get(atribute, "")
                if label == "server_ip" and self.labels[label] == "":
                    self.labels[label] = "127.0.0.1"#IP por defecto si es vacia
        dic_atributes = self.labels

    def get_tags(self):
        return self.labels.keys()
        
    def get_labels(self):
        return self.labels

    def register2file(self, dic_clients):

    #dic_clients[User] = (IP, Port, now, Expires)
    database = dic_labels["database_path"]
    # el path de fichero y musica es el archivo o la direccion??? supongo archivo
    if database == "":
        print "Empty database path in pr.xml"
        sys.exit()
    fich = open(database, "w") # TENEMOS COMPROBACION DEL FICHERO, permiso escritura
    phrase = "User" + "\t" + "IP" + "\t"+ "Port" "\t" + "Registered"
    fich.write(phrase + "Expires" + "\n")
    now = time.time()
    keys = dic_clients.keys()
    for element in keys:
        if dic_clients[element][3] > now:
            address = dic_clients[element][0]
            port = dic_clients[element][1]
            registered = dic_clients[element][2]
            expires = dic_clients[element][3]
            expires = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(exp))
            registered = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(reg))
            phrase = element + "\t" + str(address) + "\t" + str(Port) + "\t"
            fich.write(phrase + "\t" + registered + "\t" + expires + "\n")

        else:
            address = dic_clients[element][0]
            #del dic_clients[element]     ---Debemos borrar al cliente del fichero aqui o en el bye?
            print "Expiró el tiempo del cliente: (" + element,
            print " , " + address + ")"
    fich.close()

class SIPRegisterHandler(SocketServer.DatagramRequestHandler):
    """
    Servidor
    """

    def handle(self):
        """
        Método para manejar las peticiones de los clientes y
        actuar en funcion de su contenido
        """
        while 1:
            line = self.rfile.read()     
            if not line:
                self.wfile.write("SIP/2.0 400 Bad Request\r\n")
                break
            else:
                # Comprobamos el mensaje recibido del cliente
                print "PROXY-INFO: The client send us " + line
                check1 = line.find("sip:")
                check2 = line.find("@")
                check3 = line.find("SIP/2.0")
                if check1 >= 0 and check2 >= 0 and check3 >= 0:
                    lista = line.split(" ")
                    Metodo = lista[0].upper()
                    IP_client = str(self.client_address[0]) 
                    # La practica especifica que ambos UA client server estan en la misma maquina
                    # Comprobamos el método
                    if Metodo == "INVITE":
                        """INVITE sip:penny@girlnextdoor.com SIP/2.0
                        Content-Type: application/sdp
                        v=0
                        o=leonard@bigbang.org 127.0.0.1
                        s=misesion
                        t=0
                        m=audio 34543 RTP"""
                        receiver = line.split(" SIP/2.0")[0].split("sip:")[1]
                        send = line.split("s=")[0].split("o=")[1].split(" ")[0]
                        #RTP_SEND_P = line.split("m=audio ")[1].split(" ").[0]
                        print "Received INVITE from " + send + " to " + receiver
                        if dic_clients[receiver] == "":
                            self.wfile.write("SIP/2.0 404 User Not Found\r\n")
                            break
                        else:
                            parameters = dic_clients[receiver]
                            print parameters
                            
                        my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                        my_socket.connect((parameters[0], int(parameters[1])))
                        my_socket.send(line)  #reenviamos al destinatario
                        data = my_socket.recv(1024)
                        processed_data = data.split('\r\n\r\n') 
                        if processed_data[0] != "SIP/2.0 200 OK" or\
                           processed_data[1] == "":      #comprobamos OK + SDP
                            my_socket.send("SIP/2.0 400 Bad Request")
                            break
                        #my_socket.close()
                        mess = "SIP/2.0 100 Trying\r\n\r\n"
                        mess = mess + "SIP/2.0 180 Ringing\r\n\r\n" + data
                        self.wfile.write(mess)
                        print "SENDING "+ mess
                        
                    elif Metodo == "REGISTER":
                        """REGISTER sip:leonard@bigbang.org:1234 SIP/2.0
                        Expires: 3600"""
                        try:
                            User = line.split(":")[1]
                            Port = line.split(":")[2].split(" ")[0]
                            Expires = line.split("Expires: ")[1]
                            self.wfile.write("SIP/2.0 200 OK\r\n\r\n")
                        except ValueError:
                            self.wfile.write("SIP/2.0 400 Bad Request\r\n\r\n")   
                        #Guardar cliente en fichero
                        #Direccion, IP, puerto, la fecha de registro y expires
                        now = time.time()
                        Expires = int(Expires) + now
                        dic_clients[User] = (IP_client, Port, now, Expires)
                        Handler.register2file(dic_clients)
                        #                               ESCRIBIR AQUI EN EL FICHERO DE LOG DE PROXY
                        
                    elif Metodo == "ACK":
                        #ACK sip:receptor SIP/2.0
                        #enviar ACK al otro cliente con este permiso para RTP
                        receiver = line.split("sip:")[1].split(" ")[0]
                        if dic_clients[receiver] == "":
                            self.wfile.write("SIP/2.0 404 User Not Found\r\n")
                            break
                        else:
                            parameters = dic_clients[receiver]
                            print parameters
                        my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                        my_socket.connect((parameters[0], int(parameters[1])))
                        my_socket.send(line)  #reenviamos al destinatario
                        
                    elif Metodo == "BYE":
                        self.wfile.write("SIP/2.0 200 OK\r\n\r\n")
                        User = line.split(":")[1]
                        Port = line.split(":")[2].split(" ")[0]
                        del dic_clients(User)
                        print "The client " + IP_cliente + " end the conexion"

                    else:
                        self.wfile.write("SIP/2.0 405\
                         Method Not Allowed\r\n\r\n")
                else:
                    self.wfile.write("SIP/2.0 400 Bad Request\r\n")
            break


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
            """

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
    dic_clients = {}
    print dic_labels
    IP = dic_labels["server_ip"]
    PORT = int(dic_labels["server_puerto"])
    NAME = dic_labels["server_name"]
    if PORT == "" or NAME == "":
        print "Usage Error: xml file need too much proxy values"
        sys.exit()
    phrase = "\r\nStarting Server Proxy/Registrar " + NAME + " listening at "
    print phrase + str(IP) + " port " + str(PORT) + "\r\n"
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

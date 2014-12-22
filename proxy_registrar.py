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

    def register2file(self, Dic_clients):
        """
        Método reescribir el fichero con los datos del diccionario,
        revisando previamente si expiró el tiempo de alguno de los clientes
        """
        direccion_fichero = dic_labels["database_path"]
        fich = open(direccion_fichero, "w")  #con permiso de escritura de momento
        phrase = "User" + "\t" + "IP" + "\t"+ "Port" "\t" + "Registered"
        fich.write(phrase + "Expires" + "\n")
        now = time.time()
        keys = Dic_clients.keys()
        for element in keys:
            if Dic_clients[element][1] > now:
                addr = Dic_clients[element][0]
                exp = Dic_clients[element][1]
                expire = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(exp))
                fich.write(element + "\t" + str(addr) + "\t" + expire + "\n")
                                            # | REVISAR HEMOS AÑADIDO CAMPO REGISTERED ARRIBA
            else:
                address = Dic_clients[element][0]
                del Dic_clients[element]
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
                        Metodo = lista[0]
                        IP_Cliente = str(self.client_address[0])
                        # Comprobamos el método
                        if Metodo == "INVITE":
                            #Sacar puerto de RTP cliente para enviar ahí el audio
                            RTP_SEND_P = line.split('m=audio ')[1].split(" RTP")[0]
                            if RTP_SEND_P == "":
                                self.wfile.write("INVALID SDP" + '\r\n')
                            Message = "SIP/2.0 100 Trying\r\n\r\n"
                            Message = Message + "SIP/2.0 180 Ringing\r\n\r\n"
                            Message = Message + "SIP/2.0 200 OK\r\n\r\n"
                            Message = Message + "Content-Type: application/sdp\r\n"
                            Message = Message + "\r\nv=0\r\n"
                            Message = Message + "o=" + NAME + " " + IP + "\r\n"
                            Message = Message + "s=mysession \r\nt=0 \r\n"
                            Message = Message + "m=audio "+ AUDIO_PORT + " RTP\r\n"
                            if not RTP_SEND_P == "": #Asi no tabulamos lo de encima
                                self.wfile.write(Message)
                            
                        elif Metodo == "ACK":
                            os.system("chmod 777 mp32rtp")
                            Packet = "./mp32rtp -i " + IP_Cliente + " -p "
                            RTP_PORT = dic_labels["rtpaudio_puerto"]
                            Packet = Packet +  RTP_SEND_P + " < "
                            AUDIO = dic_labels["audio_path"]
                            Packet = Packet + AUDIO
                            self.wfile.write(os.system(Packet))
                        elif Metodo == "BYE":
                            self.wfile.write("SIP/2.0 200 OK\r\n\r\n")
                            print "The client " + IP_Cliente + " end the conexion"
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
    print dic_labels
    IP = dic_labels["server_ip"]
    PORT = int(dic_labels["server_puerto"])
    NAME = dic_labels["server_name"]
    if PORT == "" or NAME == "":
        print "Usage Error: xml file need too much proxy values"
        sys.exit()
    phrase = "\r\nStarting Server Proxy/Registrar " + NAME + " listening at "
    print phrase + str(IP) + " port " + str(PORT)
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

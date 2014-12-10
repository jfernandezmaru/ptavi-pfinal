#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
# Practica 6 Javier Fernandez Marugan  PTAVI

import SocketServer
import sys
import os
from xml.sax import make_parser
from xml.sax.handler import ContentHandler

"""
    Programa servidor SIP en UDP
"""


class EchoHandler(SocketServer.DatagramRequestHandler):
    """
        Clase de Servidor SIP
    """
    def handle(self):
        while 1:
            line = self.rfile.read()
            if not line:
                self.wfile.write("SIP/2.0 400 Bad Request\r\n")
                break
            else:
                # Comprobamos el mensaje recibido del cliente
                print "El cliente nos manda " + line
                check1 = line.find("sip:")
                check2 = line.find("@")
                check3 = line.find("SIP")
                check4 = line.find("/2.0")
                if check1 >= 0 and check2 >= 0 and check3 >= 0 and check4 >= 0:

                    lista = line.split(" ")
                    Metodo = lista[0]
                    IP_Cliente = str(self.client_address[0])
                    # Comprobamos el método
                    if Metodo == "INVITE":

                        message = "SIP/2.0 100 Trying\r\n\r\n"
                        message = message + "SIP/2.0 180 Ringing\r\n\r\n"
                        message = message + "SIP/2.0 200 OK\r\n\r\n"
                        self.wfile.write(message)
                    elif Metodo == "ACK":

                        os.system("chmod 777 mp32rtp")
                        Packet = "./mp32rtp -i " + IP_Cliente + " -p 23032 <"
                        Packet = Packet + AUDIO
                        os.system(Packet)
                    elif Metodo == "BYE":

                        self.wfile.write("SIP/2.0 200 OK\r\n\r\n")
                        print "Cliente " + IP_Cliente + " cierra la conexión"
                    else:

                        self.wfile.write("SIP/2.0 405\
                         Method Not Allowed\r\n\r\n")
                else:

                    self.wfile.write("SIP/2.0 400 Bad Request\r\n")
            break

if __name__ == "__main__":

    try:
        SERVER = sys.argv[1]
        PORT = int(sys.argv[2])
        if not os.access(sys.argv[3], os.F_OK):
            print "Usage: python server.py IP port audio_file"
            sys.exit()
        AUDIO = sys.argv[3]
    except ValueError:
        print "Usage: python uaserver.py config"

    print "Listening..."
    # Creamos servidor de SIP y escuchamos
    serv = SocketServer.UDPServer((SERVER, PORT), EchoHandler)
    serv.serve_forever()
    
    
class XMLHandler(ContentHandler):

    def __init__(self):

        self.labels={
            "account":["username", "passwd"],
            "uaserver":["ip", "puerto"],
            "rtpaudio":["puerto"],
            "regproxy":["ip", "puerto"],
            "log":["path"],
            "audio":["path"],
            "server":["name", "ip", "puerto"],
            "database":["path", "passwdpath"]}
        self.list=[]

    def startElement(self, name, atributes):

        dic={}
        if name in self.labels:
            dic["name"]= name
            for atribute in self.labels[name]:
                dic[atribute]=atributes.get(atribute, "")
            self.list.append(dic)

    def get_tags(self):
        return self.list

if __name__=="__main__":

    parser = make_parser()
    parser.setContentHandler(XMLHandler())
    parser.parse(open("ua1.xml"))    #Falta cambiar el nombre del fichero por el sys.argv


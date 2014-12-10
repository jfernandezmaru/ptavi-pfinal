#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
# Practica 6 Javier Fernandez Marugan  PTAVI

import SocketServer
import sys
import os
from uaclient import XMLHandler
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
                        #INCLUIR SDP CON CABECERAS
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
        FICH = sys.argv[1]
        if not os.access(sys.argv[1], os.F_OK):
            print "Usage: the file doesn't exist"
            sys.exit()
    except ValueError:
        print "Usage: python uaserver.py config"
    print "Listening..."
    # Creamos servidor de SIP y escuchamos
    #SERVER Y PORT ESTAN EN EL FICHERO XML
    serv = SocketServer.UDPServer((SERVER, PORT), EchoHandler)
    serv.serve_forever()


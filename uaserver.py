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


class XMLHandler(ContentHandler):

    def __init__(self):

        self.labels={"account_username":"", "account_passwd":"",
            "uaserver_ip":"","uaserver_puerto":"","rtpaudio_puerto":"",
            "regproxy_ip":"","regproxy_puerto":"","log_path":"",
            "audio_path":"","server_name":"","server_ip":"","server_puerto":"",
            "database_path":"","database_passwdpath":""}   

        self.atributes=["username", "passwd", "ip", "puerto", "path", "name",
                        "passwdpath"]

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
                if label == "uaserver_ip" and self.labels[label] == "":
                    self.labels[label] = "127.0.0.1"#IP por defecto si es vacia
                #print "Encuentro un atributo ~~~~~~~~~~~~~~" + atribute
                #print "Guardo de el ===========" + self.labels[label]
        dic_atributes = self.labels

    def get_tags(self):
        return self.labels.keys()
        
    def get_labels(self):
        return self.labels

class SIPHandler(SocketServer.DatagramRequestHandler):
    """
        Clase de Servidor SIP
    """
    def handle(self):
        while 1:
            line = self.rfile.read()
            if not line:
                self.wfile.write("SIP/2.0 400 Bad Request\r\n\r\n")
                break
            else:
                # Comprobamos el mensaje recibido del cliente
                print "INFORMATION: The client send us " + line
                check1 = line.find("sip:")
                check2 = line.find("@")
                check3 = line.find("SIP/2.0")

                if check1 >= 0 and check2 >= 0 and check3 >= 0:
                    lista = line.split(" ")
                    Metodo = lista[0].upper()
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
                            self.wfile.write(Message + "\r\n")
                        
                    elif Metodo == "ACK":
                        os.system("chmod 777 mp32rtp")
                        Packet = "./mp32rtp -i " + IP_Cliente + " -p "
                        RTP_PORT = dic_labels["rtpaudio_puerto"]
                        Packet = Packet +  RTP_SEND_P + " < "
                        AUDIO = dic_labels["audio_path"]
                        Packet = Packet + AUDIO
                        self.wfile.write(os.system(Packet)) 
                        # OJO estamos enviando al proxy no al cliente hay que cambiarlo (REDES)!!!!
                        
                    elif Metodo == "BYE":
                        self.wfile.write("SIP/2.0 200 OK\r\n\r\n")
                        print "The client " + IP_Cliente + " end the conexion"
                    else:
                        self.wfile.write("SIP/2.0 405\
                         Method Not Allowed\r\n\r\n")
                else:
                    self.wfile.write("SIP/2.0 400 Bad Request\r\n\r\n")
            break

if __name__ == "__main__":

    try:
        FICH = sys.argv[1]
        if not os.access(sys.argv[1], os.F_OK):
            print "Usage: the file doesn't exist"
            sys.exit()
    except ValueError:
        print "Usage: python uaserver.py config"

    parser = make_parser()
    Handler = XMLHandler()
    parser.setContentHandler(Handler)
    parser.parse(open(FICH))
    dic_labels = Handler.get_labels()
    #print dic_labels
    if dic_labels["regproxy_ip"] == "":
        print "Usage Error: xml file hasn't proxy ip value"
        sys.exit()
    SERVER = dic_labels["uaserver_ip"]
    PORT = int(dic_labels["uaserver_puerto"])
    NAME = dic_labels["account_username"]
    IP = dic_labels["uaserver_ip"]
    AUDIO_PORT = dic_labels["rtpaudio_puerto"]
    print "\r\nStarting Server at: " + str(SERVER) + " port " + str(PORT)
    # Creamos servidor de SIP y escuchamos
    #SERVER Y PORT ESTAN EN EL FICHERO XML
    serv = SocketServer.UDPServer((SERVER, PORT), SIPHandler)
    serv.serve_forever()


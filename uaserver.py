#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
# Practica FINAL Javier Fernandez Marugan  PTAVI

import SocketServer
import socket
import sys
import os
from datetime import date, datetime
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
        for count in range(len(all_labels)):
            if label == all_labels[count][0:3]:
                key_wanted = all_labels[count].split("_")[0]
                break
        for atribute in self.atributes:
            label = key_wanted + "_" + atribute
            if label in self.labels:
                self.labels[label] = attrs.get(atribute, "")
                if label == "uaserver_ip" and self.labels[label] == "":
                    self.labels[label] = "127.0.0.1"#IP por defecto si es vacia
        dic_atributes = self.labels

    def get_tags(self):
        return self.labels.keys()
        
    def get_labels(self):
        return self.labels
    def writer(self, mode, IP_PROXY, PORT_PROXY, data, fich):

        dt = datetime.now().strftime("%Y%m%d%H%M%S")
        phrase = mode + ": " + IP_PROXY + ":" + str(PORT_PROXY) + " "
        phrase = phrase + data.replace('\r\n', " ")
        fich.write(dt + " " + phrase + "\r\n") 

class SIPHandler(SocketServer.DatagramRequestHandler):
    """
        Clase de Servidor SIP
    """
    def handle(self):
        
        while 1:
            line = self.rfile.read()
            if not line:
                break
            else:
                # Comprobamos el mensaje recibido del cliente
                print "INFORMATION: The proxy/registrar send us " + line
                Handler.writer(" Receive", IP_PROXY, PORT_PROXY, line, Fich_log)
                check1 = line.find("sip:")
                check2 = line.find("@")
                check3 = line.find("SIP/2.0")
                if check1 >= 0 and check2 >= 0 and check3 >= 0:
                    lista = line.split(" ")
                    Method = lista[0].upper()
                    Auxiliar = lista[1]
                    IP_Cliente = str(self.client_address[0])
                    IP = dic_labels["uaserver_ip"]
                    if Method == "INVITE":
                        """INVITE sip:penny@girlnextdoor.com SIP/2.0
                        Content-Type: application/sdp
                        v=0
                        o=leonard@bigbang.org 127.0.0.1
                        s=misesion
                        t=0
                        m=audio 34543 RTP"""
                        RTP_SEND_P = line.split("m=audio ")[1].split(" RTP")[0]
                        UA_NAME = line.split(" sip:")[1].split(" SIP/2.0")[0]
                        dic_labels["UA_NAME"] = UA_NAME
                        RTP = line.split("o=")[1].split("s=")[0]
                        RTP_SEND_IP = RTP.split(" ")[1]
                        dic_labels["AUX_PORT"] = RTP_SEND_P
                        dic_labels["AUX_IP"] = RTP_SEND_IP
                        if RTP_SEND_P == "":
                            self.wfile.write("INVALID SDP" + '\r\n')
                        Message = "SIP/2.0 200 OK\r\n"
                        Message = Message + "Content-Type: application/sdp\r\n"
                        Message = Message + "\r\nv=0\r\n"
                        Message = Message + "o=" + NAME + " " + IP + "\r\n"
                        Message = Message + "s=mysession \r\nt=0 \r\n"
                        Message = Message + "m=audio "+ AUDIO_PORT + " RTP\r\n"
                        if not RTP_SEND_P == "": #Asi no tabulamos lo de encima
                            self.wfile.write(Message + "\r\n")
                        print "SENDING: " + Message
                        Handler.writer(" Send", IP_PROXY, PORT_PROXY,\
                         Message, Fich_log)

                    elif Method == "ACK":

                        #data = my_socket.recv(1024)
                        os.system("chmod 777 vlc")
                        phrase = "cvlc rtp://@" + IP + ":" + AUDIO_PORT + "&"
                        os.system(phrase)
                        os.system("chmod 777 mp32rtp")
                        IP = dic_labels["AUX_IP"]
                        Packet = "./mp32rtp -i " + IP.split("\r\n")[0]
                        Packet = Packet  + " -p " + dic_labels["AUX_PORT"]
                        AUDIO = dic_labels["audio_path"]
                        Packet = Packet + " < " + AUDIO
                        os.system(Packet)
                        Handler.writer(" Send", IP.split("\r\n")[0]\
                        , dic_labels["AUX_PORT"], AUDIO, Fich_log)
                        print " -AUDIO WAS SENDED-"
                        
                    elif Method == "BYE":

                        User = line.split(":")[1]
                        ph = dt + " Receive: " + User + " "
                        ph = ph + line.replace('\r\n', " ")
                        Fich_log.write(ph + "\r\n")
                        ph = dt + " Send: " + User + " SIP/2.0 200 OK"
                        Fich_log.write(ph + "\r\n")
                        Client = dic_labels["UA_NAME"]
                        print "The client " + Client + " end the conexion"
                        self.wfile.write("SIP/2.0 200 OK\r\n\r\n")
                        Handler.writer(" Receive", str(self.client_address[0])\
                        , str(self.client_address[1]), line, Fich_log)

                    elif Auxiliar == "200":

                        Auxiliar = Auxiliar
                        Handler.writer(" Receive", IP_PROXY, PORT_PROXY,\
                        Message, Fich_log)

                    else:
                        self.wfile.write("SIP/2.0 405\
                         Method Not Allowed\r\n\r\n")
                        ph = dt + " Send: " + User + "SIP/2.0 405 Method"
                        Fich_log.write(ph + " Not Allowed \r\n\r\n")
                else:
                    self.wfile.write("SIP/2.0 400 Bad Request\r\n\r\n")
                    ph = dt + " Send: " + User
                    Fich_log.write(ph +"SIP/2.0 400 Bad Request\r\n\r\n")
            break        
            
        # Sacamos esto fuera, necesitamos acceso a Fich_log desde uaclient.
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
if dic_labels["regproxy_ip"] == "":
    print "Usage Error: xml file hasn't proxy ip value"
    fich.write("Usage Error: xml file hasn't proxy ip value" + "\r\n" + "exit")
    sys.exit()
LOG = dic_labels["log_path"]
if LOG == "":
    print "Usage Error: no log path value"
    fich.write("Usage Error: no log path value" + "\r\n" + "exit")
    sys.exit()
Fich_log = open(LOG,"a")

if __name__ == "__main__":

    SERVER = dic_labels["uaserver_ip"]
    PORT = int(dic_labels["uaserver_puerto"])
    NAME = dic_labels["account_username"]
    IP = dic_labels["uaserver_ip"]
    AUDIO_PORT = dic_labels["rtpaudio_puerto"]
    IP_PROXY = dic_labels["regproxy_ip"]
    PORT_PROXY = int(dic_labels["regproxy_puerto"])
    dt = datetime.now().strftime("%Y%m%d%H%M%S")
    print "\r\nStarting Server at: " + str(SERVER) + " port " + str(PORT)
    Fich_log.write(dt + " Starting Server: " + str(SERVER) + " port " + str(PORT) + "\r\n")
    #Creamos servidor de SIP y escuchamos
    serv = SocketServer.UDPServer((SERVER, PORT), SIPHandler)
    serv.serve_forever()

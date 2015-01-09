#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
# -*- coding: utf-8 -*-
# Practica FINAL Javier Fernandez Marugan  PTAVI
import socket
import sys
import os
from uaserver import Fich_log
from uaserver import XMLHandler
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
from datetime import date, datetime

"""
Programa cliente que abre un socket a un servidor
"""


if __name__=="__main__":

    try:
        FICH = sys.argv[1]
        if not os.access(sys.argv[1], os.F_OK):
            print "Usage: the file doesn't exist"
            sys.exit()
    except ValueError:
        print "Usage: python uaclient.py config"

    parser = make_parser()
    Handler = XMLHandler()
    parser.setContentHandler(Handler)
    parser.parse(open(FICH))
    dic_labels = Handler.get_labels()
    IP_PROXY = dic_labels["regproxy_ip"]
    PORT_PROXY = int(dic_labels["regproxy_puerto"])
    NAME = dic_labels["account_username"]
    IP = dic_labels["uaserver_ip"]
    PORT = int (dic_labels["uaserver_puerto"])
    AUDIO_PORT = dic_labels["rtpaudio_puerto"]
    dt = datetime.now().strftime("%Y%m%d%H%M%S")
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    my_socket.connect((IP_PROXY, PORT_PROXY))

try:

    METHOD = sys.argv[2].upper()
    OPTION = sys.argv[3]
    Message = ""
    phrase = "\r\nStarting a client: IP " + str(IP) + " port " 
    print phrase + str(PORT) + "\r\n"
    if METHOD == "INVITE":

        DIRECTION = OPTION
        check1 = DIRECTION.find("@")
        check2 = DIRECTION.find(".")
        if check1 and check2 :
            Message = METHOD + " sip:" + DIRECTION + " SIP/2.0\r\n"
            Message = Message + "Content-Type: application/sdp \r\n\r\n"
            Message = Message + "v=0 \r\no=" + NAME + " " + IP + "\r\n"
            Message = Message + "s=misesion \r\nt=0 \r\n"
            Message = Message + "m=audio "+ AUDIO_PORT + " RTP\r\n"

        else:
            print ("Usage: direction not valid")

    elif METHOD == "BYE":

        DIRECTION = OPTION
        check1 = DIRECTION.find("@")
        check2 = DIRECTION.find(".")
        if check1 and check2 :

            Message = METHOD + " sip:" + DIRECTION + " SIP/2.0\r\n"
        else:
            print ("Usage: direction not valid")

    elif METHOD == "REGISTER":

        try:
            expires = int(OPTION)
            Message = METHOD + " sip:" + NAME + ":" + str(PORT) + " SIP/2.0\r\n"
            Message = Message + 'Expires: ' + str(expires) + '\r\n'
        except ValueError:
            print ("Usage: expires not valid")
            sys.exit()
    else:
        
        print ("Usage: method not allowed")
        sys.exit()

    Handler.writer(" Send", IP_PROXY, PORT_PROXY, Message, Fich_log)
    my_socket.send(Message + '\r\n')
    print "\r\nSENDING: " + Message
    data = my_socket.recv(1024)
    print "RECEIVING " + data
    processed_data = data.split('\r\n\r\n')
    Handler.writer(" Receive", IP_PROXY, PORT_PROXY, data, Fich_log)
    if METHOD == "INVITE" :    
        Afirm ="SIP/2.0 200 OK\r\nContent-Type: application/sdp"
        if processed_data[0] == "SIP/2.0 100 Trying" and\
           processed_data[1] == "SIP/2.0 180 Ringing" and\
           processed_data[2] == Afirm:
            name_and_IP = processed_data[3].split("o=")[1].split("s=")[0]
            name_UA = name_and_IP.split(" ")[0]
            RTP_IP = name_and_IP.split(" ")[1]
            RTP_PORT = processed_data[3].split("audio ")[1].split(" ")[0]
            LINE = 'ACK' + " sip:" + name_UA + " SIP/2.0\r\n"
            my_socket.send(LINE + '\r\n')
            Handler.writer(" Send", IP_PROXY, PORT_PROXY, LINE, Fich_log)
            phrase = "cvlc rtp://@" + IP + ":" + AUDIO_PORT + "&"
            #os.system("chmod 777 vlc")
            os.system(phrase)
            os.system("chmod 777 mp32rtp")
            Packet = "./mp32rtp -i " + RTP_IP.split("\r\n")[0] + " -p "
            Packet = Packet + RTP_PORT + " < "
            AUDIO = dic_labels["audio_path"]
            Packet = Packet + AUDIO
            Handler.writer(" Send", RTP_IP.split("\r\n")[0], RTP_PORT,\
            AUDIO, Fich_log)
            os.system(Packet)
            data = my_socket.recv(1024)  # No importa, finalizamos igualmente
            Fich_log.write(dt + " Finishing client and socket..." + "\r\n")

        elif processed_data[0][0:9] == "SIP/2.0 4":
            print "The proxy send us: " + processed_data[0]
        else:
            print processed_data[0][0:8]
            my_socket.send("SIP/2.0 400 Bad Request\r\n\r\n")
            Handler.writer(" Send", IP_PROXY, PORT_PROXY,\
            "SIP/2.0 400 Bad Request", Fich_log)
    my_socket.close()
    print "END."

except socket.error:
    print "Error: No server listening at " + IP_PROXY + " port " +\
     str(PORT_PROXY)
    Fich_log.write("Error: No server listening at" + "\r\n" + "exit")
except ValueError:
    print "Usage: python uaclient.py config method option"

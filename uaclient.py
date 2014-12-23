#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
# -*- coding: utf-8 -*-
# Practica 6 Javier Fernandez Marugan  PTAVI
"""
Programa cliente que abre un socket a un servidor
"""
import socket
import sys
import os
from uaserver import XMLHandler
from xml.sax import make_parser
from xml.sax.handler import ContentHandler


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
    #print dic_labels
    IP_PROXY = dic_labels["regproxy_ip"]
    PORT_PROXY = int(dic_labels["regproxy_puerto"])
    NAME = dic_labels["account_username"]
    IP = dic_labels["uaserver_ip"]
    PORT = int (dic_labels["uaserver_puerto"])
    AUDIO_PORT = dic_labels["rtpaudio_puerto"]
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    my_socket.connect((IP_PROXY, PORT_PROXY))   # HAY QUE PONER LA DEL PROXY CUANDO NO FALLE UA

try:
    # $python uaclient.py config metodo opción

    METHOD = sys.argv[2].upper()
    OPTION = sys.argv[3]
    Message = ""
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

    #NICK = dic_labels["account_username"]
    phrase = "\r\nStarting a client: IP " + str(IP) + " port " 
    print phrase + str(PORT) + "\r\n"
    my_socket.send(Message + '\r\n')    #borrado un '\r\n' puede que falle
    data = my_socket.recv(1024)
    print "\r\nSENDING: " + Message
    print "\r\nRECEIVING:", data
    processed_data = data.split('\r\n\r\n')
    # Si recibimos trying Ringing y OK asentimos con ACK

    if processed_data[0] == "SIP/2.0 100 Trying" and\
       processed_data[1] == "SIP/2.0 180 Ringing" and\
       processed_data[2] == "SIP/2.0 200 OK":

        name_and_IP = processed_data[3].split("o=")[1].split("s=")[0]
        name_UA = name_and_IP.split(" ")[0]
        LINE = 'ACK' + " sip:" + name_UA + " SIP/2.0\r\n"
        my_socket.send(LINE + '\r\n')
        print LINE + "ENVIADO ACK"
        """  AQUI NO ENVIAMOS RTP ????
        RTP_SEND_PORT = processed_data[4].split("m=audio ")[1].split(" RTP")[0]
        if RTP_SEND_PORT == "":
            my_socket.send("INVALID SDP" + '\r\n')
            my_socket.close()
        else:
        """
        print "--- Receiving RTP directly from other UserAgent --- \r\n"
        data = my_socket.recv(1024)
        print "Ending socket..."
        my_socket.close()
        print "END."

except socket.error:
    print "Error: No server listening at " + IP_PROXY + " port " + str(PORT_PROXY)
except ValueError:
    print "Usage: python server.py IP port audio_file"


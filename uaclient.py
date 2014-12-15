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
    print dic_labels
    SERVER = dic_labels["uaserver_ip"]
    PORT = int(dic_labels["uaserver_puerto"])
    print "Servidor " + str(SERVER) + " y puerto " + str(PORT)
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    my_socket.connect((SERVER, PORT))

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
            Message = METHOD + " sip:" + DIRECCION + " SIP/2.0\r\n" # En DIRECCION de invite va el destinatario

            # añadir SDP del INVITE

            Message = Message + "Content-Type: application/sdp \r\nv=0 \r\n"
            Message = Message + "o= " + MI_NOMBRE + MI_IP + "\r\n"
            Message = Message + "s= misesion \r\nt=0 \r\nm=audio 23032 RTP\r\n"
            Message = Message + + '\r\n'
            
        else:
            print ("Usage: direction not valid")


    elif METHOD == "BYE":

        DIRECTION = OPTION
        check1 = DIRECTION.find("@")
        check2 = DIRECTION.find(".")
        if check1 and check2 :
        
            Message = METHOD + " sip:" + DIRECCION + " SIP/2.0\r\n" # En DIRECCION de invite va el destinatario
        else:
            print ("Usage: direction not valid")

    elif METHOD == "REGISTER":
    
        EXPIRES = OPTION
        
        DIRECTION = OPTION
        check1 = DIRECTION.find("@")
        check2 = DIRECTION.find(".")
        if check1 and check2 :
            Message = METHOD + " sip:" + DIRECCION + " SIP/2.0\r\n" # En DIRECCION de invite va el destinatario
            
            # añadir SDP del INVITE
            Message = Message + + 'Expires: ' + str(EXPIRES) + '\r\n'
            
            
        else:
            print ("Usage: direction not valid")
        
        # para conseguir mi nombre hay que sacarlo del ua1 o ua2 

    my_socket.send(Message + '\r\n')    #borrado un '\r\n' puede que falle
    data = my_socket.recv(1024)
    print "Enviando: " + Message
    print "Recibido:", data
    processed_data = data.split('\r\n\r\n')
    # Si recibimos trying Ringing y OK asentimos con ACK

    if processed_data[0] == "SIP/2.0 100 Trying" and\
       processed_data[1] == "SIP/2.0 180 Ringing" and\
       processed_data[2] == "SIP/2.0 200 OK":

        LINE = 'ACK' + " sip:" + NICK + "@" + SERVER + " SIP/2.0\r\n"
        my_socket.send(LINE + '\r\n')
        data = my_socket.recv(1024)
        print "Terminando socket..."

        # Cerramos todo
        my_socket.close()
        print "Fin."

except socket.error:
    print "Error: No server listening at " + SERVER + " port " + str(PORT)
except ValueError:
    print "Usage: python server.py IP port audio_file"


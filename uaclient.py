#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
# Practica 6 Javier Fernandez Marugan  PTAVI
"""
Programa cliente que abre un socket a un servidor
"""
import socket
import sys
from xml.sax import make_parser
from xml.sax.handler import ContentHandler

try:

# $ python uaclient.py config metodo opcion

    CONFIG = sys.argv[1]
    METHOD = sys.argv[2].upper()
    OPTION = sys.argv[3]

    if METHOD == "INVITE":

           DIRECTION = OPTION
           check1 = DIRECTION.find("@")
           check2 = DIRECTION.find(".")

    elif METHOD == "BYE":

           DIRECTION = OPTION
           check1 = DIRECTION.find("@")
           check2 = DIRECTION.find(".")    

    elif METHOD == "REGISTER":
    
        EXPIRES = OPTION

    # Contenido que vamos a enviar
    LINE = METODO + " sip:" + NICK + "@" + SERVER + " SIP/2.0\r\n"
    # Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    my_socket.connect((SERVER, PORT))
    my_socket.send(LINE + '\r\n')
    data = my_socket.recv(1024)
    print "Enviando: " + LINE
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
    print "Error: No server listening at " + SERVER + "port " + str(PORT)
except ValueError:
    print "Usage: python server.py IP port audio_file"

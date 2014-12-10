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

    try:
        FICH = sys.argv[1]
        if not os.access(sys.argv[1], os.F_OK):
            print "Usage: the file doesn't exist"
            sys.exit()
    except ValueError:
        print "Usage: python uaserver.py config"

    parser = make_parser()
    parser.setContentHandler(XMLHandler())
    parser.parse(open(FICH))


try:

# $ python uaclient.py config metodo opcion

    METHOD = sys.argv[2].upper()
    OPTION = sys.argv[3]

    if METHOD == "INVITE":

       DIRECTION = OPTION
       check1 = DIRECTION.find("@")
       check2 = DIRECTION.find(".")
       
       Message = METHOD + " sip:" + DIRECCION + " SIP/2.0\r\n" # En DIRECCION de invite va el destinatario
       # añadir SDP del INVITE 
       #Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
       my_socket.send(Message + 'Expires: ' + str(EXPIRES) + '\r\n\r\n')
       
    elif METHOD == "BYE":

       DIRECTION = OPTION
       check1 = DIRECTION.find("@")
       check2 = DIRECTION.find(".")

    elif METHOD == "REGISTER":
    
        EXPIRES = OPTION
        
        # para conseguir mi nombre hay que sacarlo del ua1 o ua2 




    # Contenido que vamos a enviar
    LINE = METODO + " sip:" + NICK + "@" + SERVER + " SIP/2.0\r\n"
    # Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
    #           Message = (REGISTER + ' sip:' + LINE + ' SIP/2.0' + '\r\n')
    #           my_socket.send(Message + 'Expires: ' + str(EXPIRES) + '\r\n\r\n')
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

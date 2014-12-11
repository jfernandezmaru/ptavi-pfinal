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
from xml.sax import make_parser
from xml.sax.handler import ContentHandler

class XMLHandler(ContentHandler):

    def __init__(self):

        self.labels={"account_username":"", "account_passwd":"",
            "uaserver_ip":"","uaserver_puerto":"","rtpaudio_puerto":"",
            "regproxy_ip":"","regproxy_puerto":"","log_path":"",
            "audio_path":"","server_name":"","server_ip":"","server_puerto":"",
            "database_path":"","database_passwdpath":""}   

        """ 
        "account":["username", "passwd"],
        "uaserver":["ip", "puerto"],
        "rtpaudio":["puerto"],
        "regproxy":["ip", "puerto"],
        "log":["path"],
        "audio":["path"],
        "server":["name", "ip", "puerto"],
        "database":["path", "passwdpath"]}
        """
        self.atributes=["username", "passwd", "ip", "puerto", "path", "name",
                        "passwdpath"]

    def startElement(self, name, attrs):

        dic={}
        label = name[0:3]
        all_labels = self.labels.keys()
        key_wanted = ""
        print (all_labels)
        for count in range(len(all_labels)):    #quiero que count sea número
            if label == all_labels[count][0:3]:
                key_wanted = all_labels[count].split("_")[0]
                print "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@" + key_wanted
                break

        for atribute in self.atributes:
        
            print "############################" + atribute
            label = key_wanted + "_" + atribute
            if label in self.labels:
                self.labels[label] = attrs.get(atribute, "")
                
                print "Encuentro ~~~~~~~~~~~~~~~~~~~~~~~" + atribute
                print "Hago ====================" + self.labels[label]
        print self.labels.values()

    def get_tags(self):
        return self.labels.keys()
        
    def get_labels(self):
        return self.labels


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
    list_labels=Handler.get_tags()

try:

# $ python uaclient.py config metodo opcion
    METHOD = sys.argv[2].upper()
    OPTION = sys.argv[3]
    if METHOD == "INVITE":

        DIRECTION = OPTION
        check1 = DIRECTION.find("@")
        check2 = DIRECTION.find(".")
        if check1 and check2 :
            Message = METHOD + " sip:" + DIRECCION + " SIP/2.0\r\n" # En DIRECCION de invite va el destinatario
            # añadir SDP del INVITE 
            #Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
            my_socket.send(Message + 'Expires: ' + str(EXPIRES) + '\r\n\r\n')
        else:
            print ("Usage: direction not valid")

        Message = METHOD + " sip:" + DIRECCION + " SIP/2.0\r\n" # En DIRECCION de invite va el destinatario
        # añadir SDP del INVITE 
        #Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
        my_socket.send(Message + 'Expires: ' + str(EXPIRES) + '\r\n\r\n')

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
        
        # para conseguir mi nombre hay que sacarlo del ua1 o ua2 

    # Contenido que vamos a enviar
    #           LINE = METODO + " sip:" + NICK + "@" + SERVER + " SIP/2.0\r\n"
    # Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
    #           Message = (REGISTER + ' sip:' + LINE + ' SIP/2.0' + '\r\n')
    #           my_socket.send(Message + 'Expires: ' + str(EXPIRES) + '\r\n\r\n')

    dic_atributes = Handler.get_labels()
    SERVER = dic_atributes["server_ip"]
    PORT = dic_atributes["server_puerto"]
    
    print SERVER + "---------------" + PORT

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


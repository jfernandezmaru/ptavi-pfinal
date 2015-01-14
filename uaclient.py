#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import sys
import SocketServer
import os
import time
import socket


def MensajesLog(mensaje):
    mensaje = mensaje.split(" ")
    fich = open(cHandler.log, "a")
    msg = str(time.time()) + " " + str(mensaje) + " " + "\n"
    fich.write(msg)
    fich.close()


class ClientHandler(ContentHandler):

    def __init__(self):
        self.username = ""
        self.passwd = ""
        self.uaserver_ip = ""
        self.uaserver_puerto = 0
        self.rtp_puerto = 0
        self.regproxy_ip = ""
        self.regproxy_puerto = 0
        self.log = ""
        self.audio = ""

    def startElement(self, etiqueta, atributo):
        if etiqueta == "account":
            self.account_username = atributo.get("username", "")
            self.account_passwd = atributo.get("passwd", "")
        elif etiqueta == "uaserver":
            self.uaserver_ip = atributo.get("ip", "127.0.0.1")
            self.uaserver_puerto = atributo.get("puerto", "")
        elif etiqueta == "rtpaudio":
            self.rtpaudio_puerto = atributo.get("puerto", "")
        elif etiqueta == "regproxy":
            self.regproxy_ip = atributo.get("ip", "")
            self.regproxy_puerto = atributo.get("puerto", "")
        elif etiqueta == "log":
            self.log = atributo.get("path", "")
        elif etiqueta == "audio":
            self.audio = atributo.get("path", "")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit("Usage: python uaclient.py config method option")
    # parseamos el archivo .xml
    parser = make_parser()
    cHandler = ClientHandler()
    parser.setContentHandler(cHandler)
    parser.parse(open(sys.argv[1]))

    # cogemos los parametros pasados por argumento
    METODO = sys.argv[2]
    OPCION = sys.argv[3]

    # Dirección IP del servidor y métodos
    IP = cHandler.regproxy_ip
    PORT = int(cHandler.regproxy_puerto)

    # Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    my_socket.connect((IP, PORT))

    #LINE, LINE2 = ""
    comienzo = "Starting..."
    MensajesLog(comienzo)
    print comienzo
    #creamos LINE y LINE2 segun el tipo del metodo que pasamos como argumento
    #para hacer el envío
    if METODO == "REGISTER":
        LINE = ("REGISTER sip:" + cHandler.account_username +
                ":" + cHandler.uaserver_puerto + " SIP/2.0" + '\r\n')
        LINE2 = ("Expires: " + OPCION + '\r\n')
        print "Enviando: " + LINE + LINE2
        my_socket.send(LINE + LINE2 + '\r\n')
        envio = "Sent to " + IP + ":" + str(PORT) + ": " + LINE + LINE2
        MensajesLog(envio)
    elif METODO == "INVITE":
        LINE = "INVITE sip:" + OPCION + " SIP/2.0" + '\r\n'
        LINE2 = ("Content-Type: application/sdp" + '\r\n\r\n' + "v=0" + '\r\n'
                 + "o=" + cHandler.account_username + " " + IP + '\r\n' +
                 "s=misesion" + '\r\n' + "t=0" + '\r\n' + "m=audio " +
                 cHandler.rtpaudio_puerto + " RTP")
        print "Enviando: " + LINE + LINE2
        my_socket.send(LINE + LINE2 + '\r\n')
        LINE = "INVITE sip:" + OPCION + " SIP/2.0" + '\r\n'
        LINE2 = ("Content-Type: application/sdp" + '\r\n' + "v=0" + '\n' +
                 "o=" + cHandler.account_username + " " + IP + '\n' +
                 "s=misesion" + '\n' + "t=0" + '\n' + "m=audio " +
                 cHandler.rtpaudio_puerto + " RTP")
        envio = "Sent to " + IP + ":" + str(PORT) + ": " + LINE + LINE2
        MensajesLog(envio)
    elif METODO == "BYE":
        LINE = "BYE sip:" + OPCION + " SIP/2.0" + '\r\n'
        print "Enviando: " + LINE
        my_socket.send(LINE + '\r\n')
        envio = "Sent to " + IP + ":" + str(PORT) + ": " + LINE
        MensajesLog(envio)

    #hacemos la recepción
    try:
        data = my_socket.recv(1024)
        print 'Recibido -- ', data
    except socket.error:
        error = sys.exit("Error: No server listening at " + IP +
                         " port " + PORT)
        print error
        MensajesLog(error)

    if METODO == "REGISTER":
        recibido = ("Received from " + IP + ":" + str(PORT) + ":" +
                    "SIP/2.0 200 OK")
        MensajesLog(recibido)
    elif METODO == "INVITE":
        SDP = ("Content-Type: application/sdp" + '\r\n\r\n' + "v=0" + '\r\n' + "o=" +
               cHandler.account_username + " " + IP + '\r\n' + "s=misesion" +
               '\r\n' + "t=0" + '\r\n' + "m=audio " + cHandler.rtpaudio_puerto +
               " RTP" + '\r\n')
        if data == ("SIP/2.0 100 Trying" + '\r\n\r\n' + "SIP/2.0 180 Ringing" +
                    '\r\n\r\n' + "SIP/2.0 200 OK" + '\r\n\r\n' + SDP):
            recibido = ("Received from " + IP + ":" + str(PORT) + ":" +
                        "SIP/2.0 100 Trying " + "SIP/2.0 180 Ringing " +
                        "SIP/2.0 200 OK")
            MensajesLog(recibido)
            LINE = "ACK sip:" + OPCION + " SIP/2.0"
            print "Enviando: " + LINE
            my_socket.send(LINE + '\r\n\r\n')
            envio = "Sent to " + IP + ":" + str(PORT) + ": ACK"
            MensajesLog(envio)
            data = my_socket.recv(1024)
            encontrado = ("./mp32rtp -i " + cHandler.uaserver_ip + " -p " +
                          cHandler.rtpaudio_puerto + " < " +
                          cHandler.audio_path)
            print "Enviando audio..."
            audio = ("Sent to " + cHandler.uaserver_ip + ":" +
                     cHandler.rtpaudio_puerto + ": audio")
            MensajeLog(audio)
            os.system(encontrado)
            audio = ("Sent to " + cHandler.uaserver_ip + ":" +
                     cHandler.rtpaudio_puerto + ": envío completado")
            MensajesLog(audio)
            print "Envío completado"
            print 'Recibido -- ', data

    elif METODO == "BYE":
        recibido = ("Received from " + IP + ":" + str(PORT) + ":" +
                    "SIP/2.0 200 OK")
        MensajesLog(recibido)
        sys.exit()
    print "Terminando socket..."

    # Cerramos todo
    my_socket.close()
    fin = "Finishing."
    MensajesLog(fin)
    print "Fin."

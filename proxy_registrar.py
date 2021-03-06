#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
# Practica FINAL Javier Fernandez Marugan  PTAVI
"""
Clase (y programa principal) para un servidor Register SIP
"""
import SocketServer
import socket
import sys
import os
import time
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
from datetime import date, datetime


class XMLHandler_PROXY(ContentHandler):

    def __init__(self):

        self.labels = {"server_name": "", "server_ip": "",
                       "server_puerto": "", "database_path": "",
                       "database_passwdpath": "", "log_path": ""}

        self.atributes = ["name", "ip", "puerto", "path", "passwdpath"]

    def startElement(self, name, attrs):

        dic = {}
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
                if label == "server_ip" and self.labels[label] == "":
                    self.labels[label] = "127.0.0.1"
                elif label == "server_ip":
                    try:
                        socket.inet_aton(self.labels[label])
                    except socket.error:
                        print "Usage: Invalid IP"
                        sys.exit()
                elif label == "server_puerto":
                    try:
                        int(self.labels[label])
                    except ValueError:
                        print "Usage: Invalid Port"
                        sys.exit()
        dic_atributes = self.labels

    def get_tags(self):
        return self.labels.keys()

    def get_labels(self):
        return self.labels

    def register2file(self, dic_clients):

        database = dic_labels["database_path"]
        if database == "":
            print "Empty database path in pr.xml"
            sys.exit()
        fich = open(database, "w")
        phras = "\t" + "User" + "\t\t\t" + "IP" + "\t\t\t" + "Port" + "\t\t\t"
        fich.write(phras + "Registered" + "\t\t\t" + "Expires" + "\n")
        now = time.time()
        keys = dic_clients.keys()
        for element in keys:
            timer = dic_clients[element][3] + dic_clients[element][2]
            if timer > now:
                address = dic_clients[element][0]
                port = dic_clients[element][1]
                reg = dic_clients[element][2]
                exp = dic_clients[element][3]
                phras = element + "\t" + str(address) + "\t" + str(port) + "\t"
                fich.write(phras + "\t" + str(reg) + "\t\t" + str(exp) + "\n")

            else:
                address = dic_clients[element][0]
                del dic_clients[element]
                print "Expiró el tiempo del cliente: (" + element,
                print " , " + address + ")"
        fich.close()


class SIPRegisterHandler(SocketServer.DatagramRequestHandler):

    def handle(self):

        global LOG
        Fich_log = open(LOG, "a")
        """
        Método para manejar las peticiones de los clientes y
        actuar en funcion de su contenido
        """
        while 1:
            line = self.rfile.read()
            IP_client = str(self.client_address[0])
            Port_client = str(self.client_address[1])
            dt = datetime.now().strftime("%Y%m%d%H%M%S")
            if not line:
                self.wfile.write("SIP/2.0 400 Bad Request\r\n")
                Fich_log.write(dt + "Send: SIP/2.0 400 Bad Request\r\n")
                break
            else:
                # Comprobamos el mensaje recibido del cliente
                print "PROXY-INFO: The client send us " + line
                check1 = line.find("sip:")
                check2 = line.find("@")
                check3 = line.find("SIP/2.0")
                if check1 >= 0 and check2 >= 0 and check3 >= 0:
                    lista = line.split(" ")
                    Metodo = lista[0].upper()
                    ph = dt + " Receive: " + IP_client + ":" + Port_client +\
                        " " + line.replace('\r\n', " ")
                    Fich_log.write(ph + "\r\n")
                    if Metodo == "INVITE":
                        receiver = line.split(" SIP/2.0")[0].split("sip:")[1]
                        send = line.split("s=")[0].split("o=")[1].split(" ")[0]
                        print "Receive INVITE from " + send + " to " + receiver
                        if not receiver in dic_clients:
                            self.wfile.write("SIP/2.0 404 User Not Found\r\n")
                            ph = " Send: " + IP_client + ":" + Port_client +\
                                " SIP/2.0 404 User Not Found"
                            Fich_log.write(dt + ph + "\r\n")
                            break
                        elif not send in dic_clients:
                            ph = "SIP/2.0 436 Bad Identity Info\r\n\r\n"
                            self.wfile.write(ph)
                            ph = " Send: " + IP_client + ":" + Port_client +\
                                " SIP/2.0 436 Bad Identity Info"
                            Fich_log.write(dt + ph + "\r\n")
                            break
                        else:
                            parameters = dic_clients[receiver]
                            my_socket = socket.socket(socket.AF_INET,
                                                      socket.SOCK_DGRAM)
                            my_socket.setsockopt(socket.SOL_SOCKET,
                                                 socket.SO_REUSEADDR, 1)
                            my_socket.connect((parameters[0],
                                              int(parameters[1])))
                            my_socket.send(line)
                            ph = " Send: " + IP_client + ":" + Port_client +\
                                " " + line.replace('\r\n', " ")
                            Fich_log.write(dt + ph + "\r\n")
                            data = my_socket.recv(1024)
                            IP_cl = str(self.client_address[0])
                            PORT_cl = str(self.client_address[1])
                            processed_data = data.split('\r\n\r\n')
                            Af = "SIP/2.0 200 OK\r\n" + \
                                "Content-Type: application/sdp"
                            if processed_data[2] != Af:
                                my_socket.send("SIP/2.0 400 Bad Request")
                                ph = dt + " Send: " + IP_cl + ":" +\
                                    PORT_cl + " SIP/2.0 400 Bad Request"
                                Fich_log.write(ph + "\r\n")
                                break
                            self.wfile.write(data)
                            print "SENDING " + data
                            ph = " Send: " + IP_cl + ":" + PORT_cl +\
                                " " + data.replace('\r\n', " ")
                            Fich_log.write(dt + ph + "\r\n")

                    elif Metodo == "REGISTER":
                        try:
                            User = line.split(":")[1]
                            Port = line.split(":")[2].split(" ")[0]
                            Expires = line.split("Expires: ")[1]
                            self.wfile.write("SIP/2.0 200 OK\r\n\r\n")
                            ph = dt + " Send: " + IP_client + ":" + \
                                Port_client + " SIP/2.0 200 OK"
                            Fich_log.write(ph + "\r\n")
                        except ValueError:
                            self.wfile.write("SIP/2.0 400 Bad Request\r\n\r\n")
                            ph = dt + " Send: " + IP_client + ":" + \
                                Port_client + " SIP/2.0 400 Bad Request"
                            Fich_log.write(ph + "\r\n")
                        now = int(time.time())
                        Expires = int(Expires)
                        dic_clients[User] = (IP_client, Port, now, Expires)
                        Handler.register2file(dic_clients)

                    elif Metodo == "BYE":
                        User = line.split(":")[1].split(" ")[0]
                        if not User in dic_clients:
                            self.wfile.write("SIP/2.0 404 User Not Found\r\n")
                            ph = " Send: " + IP_client + ":" + \
                                Port_client + "SIP/2.0 404 User Not Found"
                            Fich_log.write(dt + ph + "\r\n")
                            break
                        else:
                            parameters = dic_clients[User]
                            my_socket = socket.socket(socket.AF_INET,
                                                      socket.SOCK_DGRAM)
                            my_socket.setsockopt(socket.SOL_SOCKET,
                                                 socket.SO_REUSEADDR, 1)
                            my_socket.connect((parameters[0],
                                              int(parameters[1])))
                            IP_cl = str(self.client_address[0])
                            PORT_cl = str(self.client_address[1])
                            my_socket.send(line)
                            ph = dt + " Send: " + IP_cl + ":" + PORT_cl +\
                                line.replace('\r\n', " ")
                            Fich_log.write(ph + "\r\n")
                            data = my_socket.recv(1024)
                            ph = dt + " Receive: " + IP_cl + ":" + PORT_cl + \
                                data.replace('\r\n', " ")
                            Fich_log.write(ph + "\r\n")
                            self.wfile.write(data)
                            ph = dt + " Send: " + IP_client + ":" +\
                                Port_client + data.replace('\r\n', " ")
                            Fich_log.write(ph + "\r\n")
                            print "The client " + IP_cl + ":" + PORT_cl +\
                                  " end the conexion"

                    elif Metodo == "ACK":
                        receiver = line.split("sip:")[1].split(" ")[0]
                        if not receiver in dic_clients:
                            self.wfile.write("SIP/2.0 404 User Not Found\r\n")
                            ph = dt + " Send: " + IP_client + ":" +\
                                Port_client + "SIP/2.0 404 User Not Found"
                            Fich_log.write(ph + "\r\n")
                            break
                        else:
                            parameters = dic_clients[receiver]
                            my_socket = socket.socket(socket.AF_INET,
                                                      socket.SOCK_DGRAM)
                            my_socket.setsockopt(socket.SOL_SOCKET,
                                                 socket.SO_REUSEADDR, 1)
                            my_socket.connect((parameters[0],
                                              int(parameters[1])))
                            IP_cl = str(self.client_address[0])
                            PORT_cl = str(self.client_address[1])
                            my_socket.send(line)
                            ph = dt + " Send: " + IP_cl + ":" + PORT_cl + \
                                " " + line.replace("\r\n", " ")
                            Fich_log.write(ph + "\r\n")
                    else:
                        self.wfile.write("SIP/2.0 405\
                                         Method Not Allowed\r\n\r\n")
                        ph = dt + " Send: " + IP_client + ":" + Port_client \
                            + " SIP/2.0 405 Method Not Allowed"
                        Fich_log.write(ph + "\r\n")
                else:
                    self.wfile.write("SIP/2.0 400 Bad Request\r\n")
                    Fich_log.write(dt + " Send: " + IP_client + ":"
                                   + Port_client
                                   + " SIP/2.0 400 Bad Request\r\n")
                Handler.register2file(dic_clients)
            break

if __name__ == "__main__":

    try:
        FICH = sys.argv[1]
        if not os.access(sys.argv[1], os.F_OK):
            print "Usage: the file doesn't exist"
            sys.exit()
    except ValueError:
        print "Usage: python proxy_registrar.py config"
    parser = make_parser()
    Handler = XMLHandler_PROXY()
    parser.setContentHandler(Handler)
    parser.parse(open(FICH))
    dic_labels = Handler.get_labels()
    dic_clients = {}
    IP = dic_labels["server_ip"]
    PORT = int(dic_labels["server_puerto"])
    NAME = dic_labels["server_name"]
    if PORT == "" or NAME == "":
        print "Usage Error: xml file need too much proxy values"
        sys.exit()
    LOG = dic_labels["log_path"]
    if LOG == "":
        print "Usage Error: no log path value"
        fich.write("Usage Error: no log path value" + "\r\n" + "exit")
        sys.exit()
    Fich_log = open(LOG, "a")
    dt = datetime.now().strftime("%Y%m%d%H%M%S")

    phrase = "Starting Server Proxy/Registrar " + NAME + " listening at "
    print "\r\n" + phrase + str(IP) + " port " + str(PORT) + "\r\n"
    Fich_log.write(dt + " " + phrase + str(IP) + " port " + str(PORT) + "\r\n")
    Fich_log.close()
    serv = SocketServer.UDPServer((IP, PORT), SIPRegisterHandler)
    serv.serve_forever()

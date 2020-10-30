import socket
import re
import constCS
import json
import logging
from context import lab_logging

lab_logging.setup(stream_level=logging.INFO)  # init loging channels for the lab


class Server:
    _logger = logging.getLogger("vs2lab.lab1.clientserver.Server")
    _serving = True
    dict1 = {
        "A": "111111",
        "B": "222222",
        "C": "333333",
        "D": "444444",
        "E": "555555"
    }

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((constCS.HOST, constCS.PORT))
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # prevents errors due to "addresses in use"
        self.sock.settimeout(3)  # time out in order not to block forever
        self._logger.info("Server bound to socket " + str(self.sock))

    def serve(self):
        self.sock.listen(1)
        while self._serving:  # as long as _serving (checked after connections or socket timeouts)
            try:
                (connection, address) = self.sock.accept()  # returns new socket and address of client
                while True:  # forever
                    data = connection.recv(1024)  # receive data from client
                    if not data:
                            connection.send("keine data".encode('utf-8'))
                            connection.close()  # close the connection
                            break  # stop if client stopped
                    elif data.decode('utf-8') in self.dict1:
                        connection.send(data + ": ".encode('utf-8') + self.dict1[data.decode('utf-8')].encode('utf-8'))
                    elif data.decode('utf-8') == 'getAll':
                        msg = ""
                        for i in self.dict1:
                            msg = msg + i + ": " + self.dict1[i] + " "
                        connection.send(msg.encode('utf-8'))
                    elif data.decode('utf-8') == 'exit':
                        connection.send(data)
                        connection.close()  # close the connection
                        break
                    else:
                        connection.send(data + ": keine Daten".encode('utf-8'))
            except socket.timeout:
                pass  # ignore timeouts


class Client:
    logger = logging.getLogger("vs2lab.a1_layers.client_1.Client")

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((constCS.HOST, constCS.PORT))
        self.logger.info("Client connected to socket " + str(self.sock))

    def call(self, request):

            getRequest = re.search('get\s[a-zA-Z]+' or 'Get\s[a-zA-Z]+', request)
            getAllRequest = re.search('getAll' or 'GetAll', request)
            getExitRequest = re.search('exit', request)
            if getRequest:
                str1 = request[4:]
                self.sock.send(str1.encode('utf-8'))  # send encoded string as data#
                data = self.sock.recv(1024)  # receive the response
                self.logger.info("GET REQUEST: " + data.decode('utf-8'))
                self.sock.close()  # close the connection
                return data.decode('utf-8')
            elif getAllRequest:
                self.sock.send(request.encode('utf-8'))  # send encoded string as data#
                data = self.sock.recv(1024)  # receive the response
                self.logger.info("GETALL REQUEST: " + data.decode('utf-8'))
                self.sock.close()  # close the connection
                return data.decode('utf-8')
            elif getExitRequest:
                self.sock.send('exit'.encode('utf-8'))  # send encoded string as data#
                data = self.sock.recv(1024)  # receive the response
                self.sock.close()  # close the connection
                self.logger.info("EXIT: Client down.")
                return data.decode('utf-8')
            else:
                if not request:
                    self.sock.close()  # close the connection
                    self.logger.info("NO DATA: Client down.")
                    return "keine Eingabe"
                else:
                    self.sock.send(request.encode('utf-8'))
                    data = self.sock.recv(1024)  # receive the response
                    self.sock.close()  # close the connection
                    self.logger.info("BAD DATA: Client down.")
                    return data.decode('utf-8')


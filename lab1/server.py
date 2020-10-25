import socket
import pickle
import constCS
import json

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((constCS.HOST, constCS.PORT))
s.listen(1)
dict1 = {
    "A": "111111",
    "B": "222222",
    "C": "333333",
    "D": "444444",
    "E": "555555"
}

(connection, address) = s.accept()  # returns new socket and address of client

while True:  # forever
    data = connection.recv(1024)  # receive data from client
    if not data:
        connection.send("keine data".encode('utf-8'))
        connection.close()  # close the connection
        break  # stop if client stopped
    elif data.decode('utf-8') in dict1:
        connection.send(data + ": ".encode('utf-8') + dict1[data.decode('utf-8')].encode('utf-8'))
    elif data.decode('utf-8') == 'getAll':
        json.dump(dict1, open("out.csv", "w"))
        connection.send(data + "".encode('utf-8'))
    elif data.decode('utf-8') == 'exit':
        connection.close()  # close the connection
        break
    else:
        connection.send(data + ": keine Daten".encode('utf-8'))



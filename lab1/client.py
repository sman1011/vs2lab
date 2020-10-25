import socket
import constCS
import re
import json


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((constCS.HOST, constCS.PORT))  # connect to server (block until accepted)
while True:
    request = input("Your request: ")
    getRequest = re.search('get\s[a-zA-Z]+' or 'Get\s[a-zA-Z]+', request)
    getAllRequest = re.search('getAll' or 'GetAll', request)
    getExitRequest = re.search('exit', request)
    if getRequest:
        str1 = request[4:]
        s.send(str1.encode('utf-8'))  # send encoded string as data#
        data = s.recv(1024)  # receive the response
        print(data.decode('utf-8'))  # print the result
    elif getAllRequest:
        s.send(request.encode('utf-8'))  # send encoded string as data#
        data = s.recv(1024)  # receive the response
        dataP = json.load(open("out.csv", "r"))
        for i in dataP:
          print(str(i) + ": " + str(dataP[i]))  # print the result
    elif getExitRequest:
        s.send('exit'.encode('utf-8'))  # send encoded string as data#
        data = s.recv(1024)  # receive the response
        print(data.decode('utf-8'))
        s.close()  # close the connection
        break
    else:
        if not request:
            print("keine Eingabe")
            s.close()  # close the connection
            break
        else:
            print("falsche Eingabe")
            s.send(request.encode('utf-8'))
            data = s.recv(1024)  # receive the response
            s.close()  # close the connection
            break

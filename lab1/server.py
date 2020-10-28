import socket
import csv
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
field_names = ['No', 'Name', 'Number']

adr = [
    {'No': 1, 'Name': 'A', 'Number': '111111'},
    {'No': 2, 'Name': 'B', 'Number': '222222'},
    {'No': 3, 'Name': 'C', 'Number': '333333'},
    {'No': 4, 'Name': 'D', 'Number': '444444'},
    {'No': 5, 'Name': 'E', 'Number': '555555'},
]

with open('Names.csv', 'w') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=field_names)
    writer.writeheader()
    writer.writerows(adr)
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
        json.dump(dict1, open('out.csv', 'w'))
        connection.send(data + "".encode('utf-8'))
    elif data.decode('utf-8') == 'exit':
        connection.close()  # close the connection
        break
    else:
        connection.send(data + ": keine Daten".encode('utf-8'))



import pickle
import sys
import zmq

import constPipe


def put_words(i, wrds):
    if i == '1':
        for w in wrds:
            if w not in dict_r1:
                dict_r1[w] = wrds.get(w, 0)
            else:
                dict_r1[w] = dict_r1.get(w, 0) + wrds.get(w, 0)
    else:
        for w in wrds:
            if w not in dict_r2:
                dict_r2[w] = wrds.get(w, 0)
            else:
                dict_r2[w] = dict_r2.get(w, 0) + wrds.get(w, 0)


def print_dict(dict_w):
    for d in dict_w:
        print(d + " - " + str(dict_w[d]))


me = str(sys.argv[1])
dict_r1 = {}
dict_r2 = {}
context = zmq.Context()
pull_socket = context.socket(zmq.PULL)  # create a pull socket
if me == '1':
    address1 = "tcp://" + constPipe.SRC4 + ":" + constPipe.PORT4  # 1st reducer
    pull_socket.bind(address1)  # connect to mapper 1
else:
    address2 = "tcp://" + constPipe.SRC5 + ":" + constPipe.PORT5  # how and where to connect
    pull_socket.bind(address2)  # connect to mapper 2

while True:
    work = pickle.loads(pull_socket.recv())  # receive work from a source
    put_words(me, work[1])
    if me == '1':
        print("------------------------")
        print("Dictionary 1: ")
        print("(Anfangsbuchstaben A - M)")
        print("------------------------")
        print_dict(work[1])
    else:
        print("------------------------")
        print("Dictionary 2: ")
        print("(Anfangsbuchstaben N - Z)")
        print("------------------------")
        print_dict(work[1])
#        exit(0)


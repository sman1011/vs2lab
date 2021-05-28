import zmq
import time
import pickle
import constPipe
import re
import sys


def put_words(wrds):
    for w in wrds:
        w = re.sub(r'[\.,\?,\-,\,,\!]', '', w)
        if re.match('[a-mA-M]+', w):
            if w not in dict1:
                dict1[w] = 1
            else:
                dict1[w] = dict1.get(w, 0) + 1
        elif re.match('[n-zN-Z]+', w):
            if w not in dict2:
                dict2[w] = 1
            else:
                dict2[w] = dict2.get(w, 0) + 1


me = str(sys.argv[1])
                                                  # mapper-1 how and where to connect
src = constPipe.SRC1                                          # connect to splitter
prt = constPipe.PORT1
address1 = "tcp://" + constPipe.SRC4 + ":" + constPipe.PORT4  # connect to reducer-1
address2 = "tcp://" + constPipe.SRC5 + ":" + constPipe.PORT5  # connect to reducer-2


dict1 = {}
dict2 = {}

address = "tcp://" + src + ":" + prt  # how and where to connect to splitter

context = zmq.Context()
pull_socket = context.socket(zmq.PULL)  # create a pull socket
pull_socket.connect(address)
while True:
    work = pickle.loads(pull_socket.recv())  # receive work from a splitter
    words = work[1].split()
    put_words(words)

    print(dict1)
    print(dict2)
 #       pull_socket.close()
 #       context.destroy()
#    context1 = zmq.Context()
#        context2 = zmq.Context()
    push_socket1 = context.socket(zmq.PUSH)            # create a push socket for reducer-1
    push_socket2 = context.socket(zmq.PUSH)  # create a push socket for reducer-1
    push_socket1.connect(address1)
    push_socket1.send(pickle.dumps(('1', dict1)))  # send dictionary to reducer-1
    push_socket2.connect(address2)
    push_socket2.send(pickle.dumps(('2', dict2)))  # send dictionary to reducer-2
 #   exit(0)

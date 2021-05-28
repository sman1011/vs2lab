import zmq
import pickle
import constPipe
import time

address1 = "tcp://" + constPipe.SRC1 + ":" + constPipe.PORT1  # how and where to connect
address2 = "tcp://" + constPipe.SRC1 + ":" + constPipe.PORT2  # how and where to connect
address3 = "tcp://" + constPipe.SRC3 + ":" + constPipe.PORT3  # how and where to connect

context = zmq.Context()
push_socket = context.socket(zmq.PUSH)  # create a push socket
push_socket.bind(address1)
#push_socket.bind(address2)
#push_socket.bind(address3)

with open('text.txt', 'r') as file:
    for line in file:
        line = line.rstrip()
        print(line)
        time.sleep(0.2)
        workload = line  # compute workload
        push_socket.send(pickle.dumps(('splitter', workload)))  # send workload to mapper-1, mapper-2 and mapper-3
    else:
        push_socket.send(pickle.dumps(('splitter', 'CLOSE')))  # send 'close' to mapper-1
        push_socket.send(pickle.dumps(('splitter', 'CLOSE')))  # send 'close' to mapper-2
        push_socket.send(pickle.dumps(('splitter', 'CLOSE')))  # send 'close' to mapper-3
        file.close()

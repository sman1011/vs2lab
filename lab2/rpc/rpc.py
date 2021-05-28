import constRPC
import time
import threading
from context import lab_channel
import queue


class DBList:
    def __init__(self, basic_list):
        self.value = list(basic_list)

    def append(self, data):
        self.value = self.value + [data]
        return self


class Client:

    def __init__(self):
        self.chan = lab_channel.Channel()
        self.client = self.chan.join('client')
        self.server = None

    def run(self):
        self.chan.bind(self.client)
        self.server = self.chan.subgroup('server')

    def stop(self):
        self.chan.leave('client')

    def callback(self, num):
        str_res = ""
        print('Call-back Function')
        print("       3. Message received from server!")
        str_res = str_res + " from callback-function " + str(num)
        return str_res

    def append(self, data, db_list):
        assert isinstance(db_list, DBList)
        msglst = (constRPC.APPEND, data, db_list)  # message payload
        que = queue.Queue()
        self.chan.send_to(self.server, msglst)  # send msg to server
        ack = self.chan.receive_from(self.server)
        main_thread = threading.Thread(target=Client.main_fkt, args=(self, ))
        t = threading.Thread(target=lambda q, arg1: q.put(self.chan.receive_from(arg1)), args=(que, self.server))
        t.start()
        print("       1. wait for ACK from server:")
        if ack[1] == constRPC.OK:
            print("ACK: OK")
            print("       2. waiting for message from server...")
            main_thread.start()
            t.join()
            result = que.get()
            print(result[1].value)
            callback = Client.callback(self, result[1].value)
            main_thread.join()
            return callback  # pass it to caller
        else:
            print("FAIL")
            return constRPC.FAIL

    def main_fkt(self):
        print('The main program continues to run in foreground.')
        for i in range(15):
            time.sleep(1)
            print("-" + str(i) + "-")


class Server:
    def __init__(self):
        self.chan = lab_channel.Channel()
        self.server = self.chan.join('server')
        self.timeout = 3

    @staticmethod
    def append(data, db_list):
        assert isinstance(db_list, DBList)  # - Make sure we have a list
        return db_list.append(data)

    def run(self):
        self.chan.bind(self.server)
        while True:
            msgreq = self.chan.receive_from_any(self.timeout)  # wait for any request
            if msgreq is not None:
                client = msgreq[0]  # see who is the caller
                msgrpc = msgreq[1]  # fetch call & parameters
                if constRPC.APPEND == msgrpc[0]:  # check what is being requested
                    self.chan.send_to({client}, constRPC.OK)  # return ack
                    print("Processing request...")
                    result = self.append(msgrpc[1], msgrpc[2])  # do local call
                    for i in range(10):
                        print("server working... " + str(i))  # pretend working
                        time.sleep(1)
                    print("Return response.")
                    self.chan.send_to({client}, result)  # return response
                else:
                    pass  # unsupported request, simply ignore


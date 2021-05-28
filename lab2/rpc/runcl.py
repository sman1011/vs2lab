import os
import rpc
import logging
from context import lab_logging
import time

os.system('cls')
lab_logging.setup(stream_level=logging.INFO)


def callback():
    str_res = ""
    print('Call-back Function')
    print("       3. Message received from server!")
    str_res = str_res + " from callback-function "
    return str_res


def main_fkt():
    print('The main program continues to run in foreground.')
    for i in range(15):
        time.sleep(1)
        print("-" + str(i) + "-")


cl = rpc.Client()
cl.run()
base_list = rpc.DBList({'foo'})
result_list = cl.append('bar', base_list)
print("Result: {}".format(result_list))
cl.stop()

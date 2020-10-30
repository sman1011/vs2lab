import logging
import threading
import unittest
import clientserver
from context import lab_logging

lab_logging.setup(stream_level=logging.INFO)


class TestEchoService(unittest.TestCase):
    _server = clientserver.Server()  # create single server in class variable
    _server_thread = threading.Thread(target=_server.serve)  # define thread for running server

    @classmethod
    def setUpClass(cls):
        cls._server_thread.start()  # start server loop in a thread (called only once)

    def setUp(self):
        super().setUp()
        self.client = clientserver.Client()  # create new client for each test

    def test_srv_getA(self):  # each test_* function is a test
        msg = self.client.call("get A")
        self.assertEqual(msg, 'A: 111111')

    def test_srv_getB(self):  # each test_* function is a test
        msg = self.client.call("get B")
        self.assertEqual(msg, 'B: 222222')

    def test_srv_getBadData(self):  # each test_* function is a test
        msg = self.client.call("qwerty")
        self.assertEqual(msg, 'qwerty: keine Daten')

    def test_srv_getAll(self):  # each test_* function is a test
        msg = self.client.call("getAll")
        self.assertEqual(msg, "A: 111111 B: 222222 C: 333333 D: 444444 E: 555555 ")

    def test_srv_getExit(self):  # each test_* function is a test
        msg = self.client.call("exit")
        self.assertEqual(msg, 'exit')

    @classmethod
    def tearDownClass(cls):
        cls._server._serving = False  # break out of server loop
        cls._server_thread.join()  # wait for server thread to terminate


if __name__ == '__main__':
    unittest.main()

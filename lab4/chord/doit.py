""" 
Chord Application
- defines a DummyChordClient implementation
- sets up a ring of chord_node instances
- Starts up a DummyChordClient
- nodes and client run in separate processes
- multiprocessing should work on unix and windows
"""

import logging
import sys
import multiprocessing as mp
import random
import time
import chordnode as chord_node
import constChord
from context import lab_channel, lab_logging

lab_logging.setup(stream_level=logging.INFO)


class DummyChordClient:
    """A dummy client template with the channel boilerplate"""

    def __init__(self, channel):
        self.channel = channel
        self.node_id = channel.join('client')
        self.key = random.randint(0, pow(2, constChord.N_BITS) - 1)
        self.node_list = []
        self.random_node = -1

    def enter(self):
        self.channel.bind(self.node_id)

    def run(self):
        print("Client - id: " + self.node_id)
        print("Key: {}".format(self.key))
        for i in list(self.channel.channel.smembers('node')):
            self.node_list.append(i.decode())
        random_list = random.sample(self.node_list, k=1)
        self.random_node = random_list[0]
        print("Random-Node: {}".format(self.random_node))
        self.channel.send_to({j.decode() for j in list(self.channel.channel.smembers('node'))
                              if j.decode() == self.random_node}, (constChord.LOOKUP_REQ, self.key))
        message = self.channel.receive_from_any()
        sender: str = message[0]  # Identify the sender
        reply: str = message[1]
        if reply[0] == constChord.LOOKUP_REP:
            print("------------------------")
            print("GESUCHTER KNOTEN: {}".format(sender))
            print("------------------------")
            self.node_list.sort(reverse=False)
            print("Node-List: {}".format(self.node_list))
        self.channel.send_to(  # a final multicast
            {i.decode() for i in list(self.channel.channel.smembers('node'))},
            constChord.STOP)


def create_and_run(num_bits, node_class, enter_bar, run_bar):
    """
    Create and run a node (server or client role)
    :param num_bits: address range of the channel
    :param node_class: class of node
    :param enter_bar: barrier syncing channel population 
    :param run_bar: barrier syncing node creation
    """
    chan = lab_channel.Channel(n_bits=num_bits)
    node = node_class(chan)
    enter_bar.wait()  # wait for all nodes to join the channel
    node.enter()  # do what is needed to enter the ring
    run_bar.wait()  # wait for all nodes to finish entering
    node.run()  # start operating the node


if __name__ == "__main__":  # if script is started from command line
    m = 6  # Number of bits for linear names
    n = 8  # Number of nodes in the chord ring

    # Check for command line parameters m, n.
    if len(sys.argv) > 2:
        m = int(sys.argv[1])
        n = int(sys.argv[2])

    # Flush communication channel
    chan = lab_channel.Channel()
    chan.channel.flushall()

    # we need to spawn processes for support of windows
    mp.set_start_method('spawn')

    # create barriers to synchronize bootstrapping
    bar1 = mp.Barrier(n+1)  # Wait for channel population to complete
    bar2 = mp.Barrier(n+1)  # Wait for ring construction to complete

    # start n chord nodes in separate processes
    children = []
    for i in range(n):
        nodeproc = mp.Process(
            target=create_and_run,
            name="ChordNode-" + str(i),
            args=(m, chord_node.ChordNode, bar1, bar2))
        children.append(nodeproc)
        nodeproc.start()
    # spawn client proc and wait for it to finish
    clientproc = mp.Process(
        target=create_and_run,
        name="ChordClient",
        args=(m, DummyChordClient, bar1, bar2))
    clientproc.start()
    clientproc.join()

    # wait for node processes to finish
    for nodeproc in children:
        nodeproc.join()

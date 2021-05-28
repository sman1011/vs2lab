import random
import logging
import time

# coordinator messages
from const2PC import VOTE_REQUEST, GLOBAL_COMMIT, GLOBAL_ABORT
# participant decissions
from const2PC import LOCAL_SUCCESS, LOCAL_ABORT, ERROR, ABORT
# participant messages
from const2PC import VOTE_COMMIT, VOTE_ABORT, NEED_DECISION
# coordinator & participant messages
from const2PC import PREPARE_COMMIT, READY_COMMIT, READY_ABORT
# misc constants
from const2PC import TIMEOUT

import stablelog
import coordinator


class Participant:
    """
    Implements a two phase commit participant.
    - state written to stable log (but recovery is not considered)
    - in case of coordinator crash, participants mutually synchronize states
    - system blocks if all participants vote commit and coordinator crashes
    - allows for partially synchronous behavior with fail-noisy crashes
    """

    def __init__(self, chan):
        self.channel = chan
        self.participant = self.channel.join('participant')
        self.stable_log = stablelog.create_log(
            "participant-" + self.participant)
        self.logger = logging.getLogger("vs2lab.lab6.2pc.Participant")
        self.coordinator = {}
        self.all_participants = {}
        self.state = 'NEW'


    @staticmethod
    def _do_work():
        # Simulate local activities that may succeed or not ---------------------------crash in state INIT ----------
        return LOCAL_ABORT if random.random() > 3/3 else LOCAL_SUCCESS

    def _enter_state(self, state):
        self.stable_log.info(state)  # Write to recoverable persistant log file
        self.logger.info("Participant {} entered state {}."
                         .format(self.participant, state))
        self.state = state

    def init(self):
        self.channel.bind(self.participant)
        self.coordinator = self.channel.subgroup('coordinator')
        self.all_participants = self.channel.subgroup('participant')
        self._enter_state('INIT')  # Start in local INIT state.

    def run(self):
        # Wait for start of joint commit
        msg = self.channel.receive_from(self.coordinator, TIMEOUT)
        if not msg:  # Crashed coordinator - give up entirely
            # decide to locally abort (before doing anything)
            decision = ABORT
            self._enter_state('ABORT')
            self.channel.send_to(self.all_participants, GLOBAL_ABORT)
            return "Participant {} terminated in state ABORT".format(self.participant)
        else:  # Coordinator requested to vote, joint commit starts
            assert msg[1] == VOTE_REQUEST

            # Firstly, come to a local decision
            decision = self._do_work()  # proceed with local activities

            # If local decision is negative,
            # then vote for abort and quit directly
            if decision == LOCAL_ABORT:
                self._enter_state('ABORT')
                self.channel.send_to(self.coordinator, VOTE_ABORT)
                return "Participant {} terminated in state ABORT".format(self.participant)

            # If local decision is positive,
            # we are ready to proceed the joint commit
            else:
                assert decision == LOCAL_SUCCESS
                self.channel.send_to(self.coordinator, VOTE_COMMIT)
                self._enter_state('READY')
                msg_1 = self.channel.receive_from(self.coordinator, TIMEOUT)
                crash_ready = ERROR
                if random.random() > 10 / 10:  # simulate a crash  -----------------------crash in state READY ------
                    crash_ready = LOCAL_ABORT
                if not msg_1:  # Crashed coordinator

                    # Ask all processes for their decisions
                    self.channel.send_to(self.all_participants, NEED_DECISION)
####################################################   READY   ################################################
                    self.new_coordinator = min(self.all_participants)   # <--------- new coordinator
                    print("--{}--".format(self.all_participants))

                    while True:
                        if self.participant == self.new_coordinator:
                            self.channel.send_to(self.all_participants, 'WAIT')
                            break
                        else:
                            new_msg = self.channel.receive_from_any()
                            if new_msg[1] == 'WAIT':
                                if self.state == 'INIT':
                                    self._enter_state('READY')
                                    self.channel.send_to(self.new_coordinator, VOTE_COMMIT)
                                break

                    self.channel.send_to(self.all_participants, GLOBAL_ABORT)
                    while True:
                        msg = self.channel.receive_from_any()
                        if msg[1] in [GLOBAL_ABORT]:
                            self._enter_state('ABORT')
                            break

                    exit(0)

##################################################################################################################
                if msg_1[1] == GLOBAL_ABORT:
                    self._enter_state('ABORT')
                    self.channel.send_to(self.coordinator, GLOBAL_ABORT)
                    return "Participant {} terminated in state ABORT. Reason: Global abort from coordinator.".format(
                        self.participant)
                elif msg_1[1] == PREPARE_COMMIT:
                    # Notify coordinator about local commit vote
                    self.channel.send_to(self.coordinator, READY_COMMIT)
                    self._enter_state('PRECOMMIT')
                # Wait for coordinator to notify the final outcome
                msg = self.channel.receive_from(self.coordinator, TIMEOUT)
                if not msg:  # Crashed coordinator
                    # Ask all processes for their decisions
                    self.channel.send_to(self.all_participants, NEED_DECISION)
######################################################    PRECOMMIT   ################################################
                    while True:
                        msg = self.channel.receive_from_any()
                        # If someone reports a final decision,
                        # we locally adjust to it
                        if msg[1] in [NEED_DECISION]:
                            p = msg[0]
                            decision = "Koordinator auswählen"
                            print("decision: {} - {} - {} - {}".format(p, decision, self.state, self.participant))
                            self.new_coordinator = min(self.all_participants)
                            print("new coord: {}".format(self.new_coordinator))
                            if self.participant == self.new_coordinator:
                                print("new coord: {} -> {}".format(self.new_coordinator, self.state))
                            break
                    while True:
                        # if self.new_coordinator is not None:
                        if self.participant == self.new_coordinator:
                            self.channel.send_to(self.all_participants, 'PRECOMMIT')
                            break
                        else:
                            new_msg = self.channel.receive_from_any()
                            if new_msg[1] == 'PRECOMMIT':
                                print("{}->{}".format(self.participant, self.state))
                                if self.state == 'READY':
                                    self._enter_state('PRECOMMIT')
                                    self.channel.send_to(self.new_coordinator, READY_COMMIT)
                                break
                    while True:
                        state_msg = self.channel.receive_from_any()
                        print("STATE: {} - {}".format(state_msg[1], state_msg[0]))
                        break
                    self.channel.send_to(self.all_participants, GLOBAL_COMMIT)
                    while True:
                        msg = self.channel.receive_from_any()
                        if msg[1] in [GLOBAL_COMMIT]:
                            self._enter_state('COMMIT')
                            break
                    exit(0)
######################################################################################################################
                else:  # Coordinator came to a decision
                    decision = msg[1]
        if decision == GLOBAL_COMMIT:
            self._enter_state('COMMIT')

        # Help any other participant when coordinator crashed
        num_of_others = len(self.all_participants) - 1
        while num_of_others > 0:
            num_of_others -= 1
            msg = self.channel.receive_from(self.all_participants, TIMEOUT * 2)
            if msg and msg[1] == NEED_DECISION:
                self.channel.send_to({msg[0]}, decision)

        return "Participant {} terminated in state {} due to {}.".format(
            self.participant, self.state, decision)

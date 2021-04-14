# Standard library imports
import unittest

# Third party imports

# Local application imports
from tennis_ball_tracker import session


class test_session(unittest.TestCase):
    def test_push_pull(self):
        IP = "127.0.0.1"
        PORT = 5612
        MSG_SENT = {"message": "Testing the connection"}

        # Start the push session
        push_session = session.zmq_push_session_t(PORT)
        push_session.start(IP)
        
        # Start the pull session
        pull_session = session.zmq_pull_session_t(PORT)
        pull_session.start(IP)

        # Send a message
        push_session.send(MSG_SENT)

        # Receive the message
        msg_received = pull_session.receive(True)

        self.assertEquals(MSG_SENT, msg_received)

    @unittest.skip("Not working")
    def test_pub_sub(self):
        IP = "127.0.0.1"
        PORT = 5612
        TOPIC = "test"
        MSG_SENT = {"message": "Testing the connection"}

        # Start the pub session
        pub_session = session.zmq_publish_session_t(PORT)
        pub_session.start(IP)
        
        # Start the sub sessions
        sub_session1 = session.zmq_subscription_session_t([TOPIC], PORT)
        sub_session1.start(IP)
        
        # sub_session2 = session.zmq_subscription_session_t([TOPIC], PORT)
        # sub_session2.start(IP)

        # Send a message
        pub_session.send(MSG_SENT, TOPIC)

        # Receive the message
        msg_received_1 = sub_session1.receive(TOPIC)
        # msg_received_2 = sub_session2.receive(TOPIC)

        self.assertEquals(MSG_SENT, msg_received_1)
        # self.assertEquals(MSG_SENT, msg_received_2)

    def test_rep_req(self):
        IP = "127.0.0.1"
        PORT = 5612
        REQ_SENT = {"message": "Testing the connection"}
        REQ_RESPONSE = {"message": "Received the message"}

        # Start the rep session
        rep_session = session.zmq_reply_session_t(PORT)
        rep_session.start(IP)
        
        # Start the req sessions
        req_session = session.zmq_request_session_t(PORT)
        req_session.start(IP)
        
        # Send a request
        req_session.send(REQ_SENT)

        # Receive the request and respond
        req_received = rep_session.receive(True)
        self.assertEquals(REQ_SENT, req_received)
        rep_session.send(REQ_RESPONSE)

        # Receive the response
        resp_received = req_session.receive(True)
        self.assertEquals(REQ_RESPONSE, resp_received)

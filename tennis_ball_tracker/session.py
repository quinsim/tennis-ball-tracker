# Standard library imports
import abc

# Third party imports
import zmq
import msgpack

# Local application imports

class session_t(object):
    """
    Class that defines the requirements for a session.

    Args:
        port: (int): The session's port.
    """
    def __init__(
        self,
        port,
    ):
        self.port = port
        self.socket = None

    @property
    def is_connected(self):
        """
        Determins if the socket is currently connected.

        Returns:
            bool: True if connected, False otherwise
        """
        return bool(self.socket)

    def serialize(self, request):
        """
        Serializes a message using msgpack.

        Args:
            request (): The request.
        
        Returns:
            str: A string of bytes.
        """
        return msgpack.packb(request)

    def deserialize(self, sbuf):
        """
        Deserialize a message using msgpack.Unpacker.

        Args:
            sbuf ():

        Returns:
            : The message.
        """
        unpacker = msgpack.Unpacker()
        unpacker.feed(sbuf)

        msgs = [unpacked for unpacked in unpacker]
        return msgs[0] if len(msgs) else None

    @abc.abstractmethod
    def start(self, ip_address):
        """
        Starts a connection to the session.

        Args:
            ip_address (): The ip address to connect to.
        """
    
    @abc.abstractmethod
    def stop(self):
        """Stops the connection to the session."""

    @abc.abstractmethod
    def send(self, request):
        """
        Sends a message to the connected socket.

        Args:
            request (): The request to send.
        """

    @abc.abstractmethod
    def receive(self):
        """
        Receives a respose from the connected socket.

        Returns:
            : The message received
        """

    def send_receive(self, request):
        """
        Sends a message and receives a response from the connected socket.

        Args:
            request ():
        
        Returns:
            : The message received.
        """
        self.send(request)
        return self.receive()

    
class zmq_session_t(session_t):
    """
    Defines a zmq session.

    This class uses the zmq library for connecting.

    Args:
        port: (int): The session's port.

    Attributes:
        SESSION_TYPE (int): The session type.
    """

    SESSION_TYPE = None

    def start(self, ip_address):
        if not self.is_connected:
            context = zmq.Context()
            self.socket = context.socket(self.SESSION_TYPE)
            self.socket.connect("tcp://{ip_address}:{port}".format(ip_address=ip_address, port=self.port))

    def stop(self):
        if self.is_connected:
            self.socket.close()
        self.socket = None


class zmq_publish_session_t(zmq_session_t):
    """
    Defines a zmq publish session.

    This class uses the zmq library for connecting to a publish session.

    Args:
        port: (int): the session's port.
    """

    SESSION_TYPE = zmq.PUB

    def start(self, ip_address):
        if not self.is_connected:
            context = zmq.Context()
            self.socket = context.socket(self.SESSION_TYPE)
            self.socket.bind("tcp://{ip_address}:{port}".format(ip_address=ip_address, port=self.port))

    def send(self, request, topic):
        """
        Sends a message to the connected socket.

        Args:
            request (): The request to send.
            topic (str): The topic to send under.
        """
        self.socket.send(self.serialize(topic), flags=zmq.SNDMORE)
        self.socket.send(self.serialize(request))
    
    def receive(self):
        """ZMQ Pub sessions do not support receiving requests."""
        raise NotImplementedError("ZMQ Pub sessions do not support receiving requests.")

    def send_receive(self, request):
        """ZMQ Pub sessions do not support receiving requests."""
        raise NotImplementedError("ZMQ Pub sessions do not support receiving requests.")


class zmq_subscription_session_t(zmq_session_t):
    """
    Defines a zmq subscription session.

    This class uses the zmq library for connecting to a subscription session.

    Args:
        topics: (List[str]): list of topics to subscribe to.
        port: (int): the session's port.
    """

    SESSION_TYPE = zmq.SUB

    def __init__(
        self,
        topics,
        *args
    ):
        super(zmq_subscription_session_t, self).__init__(*args)
        self.topics = topics

    def subscribe(self, topic):
        """
        Subscribes to the given topic.

        Args:
            topic (str): The topic to subscribe to.
        """
        self.socket.setsockopt(zmq.SUBSCRIBE, bytes(topic))

    def start(self, ip_address):
        super(zmq_subscription_session_t, self).start(ip_address)
        for topic in self.topics:
            self.subscribe(topic)

    def send(self, request):
        """ZMQ Sub sessions do not support sending requests."""
        raise NotImplementedError("ZMQ Sub sessions do not support sending requests.")

    def receive(
        self, search_for_topic = None, timeout_ms = None):
        """
        Polls the socket for any of the subscribed topics.

        Will return the first message it receives. If no timeout is specified,
        the method will wait for the next response.

        Args:
            search_for_topic (str, optional): Poll for a specific topic
            timeout_ms (int, optional): Timeout in milliseconds to error out if a message is not received. Defaults to None.

        Returns:
            Tuple[str, ]: [The topic, the message].
        """
        flags = 0

        topic = str(self.socket.recv(flags=flags))
        sbuf = self.socket.recv(flags=flags)
        return self.deserialize(sbuf)


        # topic = str(self.socket.recv())
        # sbuf = self.socket.recv()
        # poller = zmq.Poller()
        # poller.register(self.socket, zmq.POLLIN)

        # socks = dict(poller.poll(timeout=timeout_ms))
        # if self.socket in socks and socks[self.socket] == zmq.POLLIN:
        #     topic = str(self.socket.recv())
        #     sbuf = self.socket.recv()
        #     if search_for_topic is not None:
        #         if search_for_topic != topic:
        #             return self.receive(search_for_topic, timeout_ms)
        #     return topic, self.deserialize(sbuf)
        # else:
        #     return self.receive(search_for_topic, timeout_ms)

    def send_receive(self, request):
        """ZMQ Sub sessions do not support sending requests."""
        raise NotImplementedError("ZMQ Sub sessions do not support sending requests.")


class zmq_push_session_t(zmq_session_t):
    """
    Defines a zmq pull session.

    This class uses the zmq library for connecting to a pull session.

    Args:
        port: (int): the session's port.
    """

    SESSION_TYPE = zmq.PUSH

    def start(self, ip_address):
        if not self.is_connected:
            context = zmq.Context()
            self.socket = context.socket(self.SESSION_TYPE)
            self.socket.bind("tcp://{ip_address}:{port}".format(ip_address=ip_address, port=self.port))

    def send(self, request):
        """
        Sends a message to the connected socket.

        Args:
            request (): The request to send.
        """
        self.socket.send(self.serialize(request))

    def receive(self):
        """ZMQ Push sessions do not support receiving requests."""
        raise NotImplementedError("ZMQ Push sessions do not support receiving requests.")

    def send_receive(self, request):
        """ZMQ Push sessions do not support receiving requests."""
        raise NotImplementedError("ZMQ Push sessions do not support receiving requests.")


class zmq_pull_session_t(zmq_session_t):
    """
    Defines a zmq pull session.

    This class uses the zmq library for connecting to a pull session.

    Args:
        port: (int): the session's port.
    """

    SESSION_TYPE = zmq.PULL

    def send(self, request):
        """ZMQ Pull sessions do not support sending requests."""
        raise NotImplementedError("ZMQ Pull sessions do not support sending requests.")

    def receive(self, block = False):
        """
        Receives a response from the connected socket.

        Args:
            block (bool, optional): Wait for a response from the socket if there is not one ready. Defaults to False.

        Returns:
            : The message received.
        """
        flags = zmq.NOBLOCK if not block else 0

        sbuf = self.socket.recv(flags=flags)
        return self.deserialize(sbuf)

    def send_receive(self, request):
        """ZMQ Pull sessions do not support sending requests."""
        raise NotImplementedError("ZMQ Pull sessions do not support sending requests.")


class zmq_reply_session_t(zmq_session_t):
    """
    Defines a zmq reply session.

    This class uses the zmq library for connecting to a reply session.

    Args:
        port: (int): the session's port.
    """

    SESSION_TYPE = zmq.REP

    def start(self, ip_address):
        if not self.is_connected:
            context = zmq.Context()
            self.socket = context.socket(self.SESSION_TYPE)
            self.socket.bind("tcp://{ip_address}:{port}".format(ip_address=ip_address, port=self.port))

    def send(self, request):
        self.socket.send(self.serialize(request))

    def receive(self, block = False):
        """
        Receives a response from the connected socket.

        Args:
            block (bool, optional): Wait for a response from the socket if there is not one ready. Defaults to False.

        Returns:
            : The message received.
        """
        flags = zmq.NOBLOCK if not block else 0

        sbuf = self.socket.recv(flags=flags)
        return self.deserialize(sbuf)

    def send_receive(self, request, block = False):
        """
        Sends a request and receives a response from the connected socket.

        Args:
            request (): The request to send.
            block (bool, optional): Wait for a response from the socket if there is not one ready. Defaults to False.

        Returns:
            : The message received
        """
        self.send(request)
        return self.receive(block)


class zmq_request_session_t(zmq_session_t):
    """
    Defines a zmq request session.

    This class uses the zmq library for connecting to a request session.

    Args:
        port: (int): the session's port.
    """

    SESSION_TYPE = zmq.REQ

    def send(self, request):
        self.socket.send(self.serialize(request))

    def receive(self, block = False):
        """
        Receives a response from the connected socket.

        Args:
            block (bool, optional): Wait for a response from the socket if there is not one ready. Defaults to False.

        Returns:
            : The message received.
        """
        flags = zmq.NOBLOCK if not block else 0

        sbuf = self.socket.recv(flags=flags)
        return self.deserialize(sbuf)

    def send_receive(self, request, block = False):
        """
        Sends a request and receives a response from the connected socket.

        Args:
            request (): The request to send.
            block (bool, optional): Wait for a response from the socket if there is not one ready. Defaults to False.

        Returns:
            : The message received
        """
        self.send(request)
        return self.receive(block)

import asyncio
from .exceptions import AMQPError, Deleted
from .message import Message, IncomingMessage
from .connection import Connection
from .channel import Channel
from .exchange import Exchange
from .queue import Queue, QueueBinding, Consumer


@asyncio.coroutine
def connect(host='localhost',
            port=5672,
            username='guest', password='guest',
            virtual_host='/',
            on_connection_close=None, *,
            loop=None, **kwargs):
    """
    Connect to an AMQP server on the given host and port.

    Log in to the given virtual host using the supplied credentials.
    This function is a :ref:`coroutine <coroutine>`.

    :param str host: the host server to connect to.
    :param int port: the port which the AMQP server is listening on.
    :param str username: the username to authenticate with.
    :param str password: the password to authenticate with.
    :param str virtual_host: the AMQP virtual host to connect to.
    :param func on_connection_close: function called after connection lost.

    Further keyword arguments are passed on to :meth:`create_connection() <asyncio.BaseEventLoop.create_connection>`.

    :return: the :class:`Connection` object.
    """
    from .protocol import AMQP
    from .routing import Dispatcher
    from .connection import ConnectionInfo, open_connection

    loop = asyncio.get_event_loop() if loop is None else loop

    dispatcher = Dispatcher()
    protocol_factory = lambda: AMQP(dispatcher, loop, close_callback=on_connection_close)
    transport, protocol = yield from loop.create_connection(protocol_factory, host=host, port=port, **kwargs)

    connection = yield from open_connection(loop, protocol, dispatcher, ConnectionInfo(username, password, virtual_host))
    return connection


@asyncio.coroutine
def connect_and_open_channel(host='localhost',
                             port=5672,
                             username='guest', password='guest',
                             virtual_host='/',
                             on_connection_close=None, *,
                             loop=None, **kwargs):
    """
    Connect to an AMQP server and open a channel on the connection.
    This function is a :ref:`coroutine <coroutine>`.

    Parameters of this function are the same as :func:`connect`.

    :return: a tuple of ``(connection, channel)``.

    Equivalent to::

        connection = yield from connect(host, port, username, password, virtual_host, loop=loop, **kwargs)
        channel = yield from connection.open_channel()
        return connection, channel
    """
    connection = yield from connect(host, port, username, password, virtual_host, loop=loop, **kwargs)
    channel = yield from connection.open_channel()
    return connection, channel

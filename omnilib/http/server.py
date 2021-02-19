import abc
import threading
from enum import Enum, unique
from http.server import BaseHTTPRequestHandler, HTTPServer

from ..util import Singleton


@unique
class HTTPMethod(Enum):
    """HTTP Verbs enum"""
    GET = 1
    POST = 2
    PATCH = 3


class HTTPHandlerRegistry(object):
    """Registry for an HTTP Server.

    This enables adding and removing HTTP Request handlers on the go.
    Supports regular handlers for responding to requests on a specific path.
    Supports default handlers for various HTTP methods.
    """

    def __init__(self):
        self.request_handlers = {}
        self.default_request_handlers = {}

    def register_request_handler(self, method, path, handler):
        if method not in self.request_handlers:
            self.request_handlers[method] = {}
        self.request_handlers[method][path] = handler

    def register_default_request_handler(self, method, handler):
        self.default_request_handlers[method] = handler

    def get_handler(self, method, path):
        request_handler = self.get_request_handler(method, path)
        if request_handler:
            return request_handler
        default_handler = self.get_default_request_handler(method)
        if default_handler:
            return default_handler
        else:
            return None

    def get_request_handler(self, method, path):
        return self.request_handlers.get(method, {}).get(path, None)

    def get_default_request_handler(self, method):
        return self.default_request_handlers.get(method, None)

    def deregister_request_handler(self, method, path):
        if self.get_request_handler(method, path):
            del self.request_handlers[method][path]

    def deregister_default_request_handler(self, method):
        if self.get_default_request_handler(method):
            del self.default_request_handlers[method]


class StatelessHTTPHandler(abc.ABC):
    """An abstract class to be extended by stateless HTTP Request Handlers.

    The instance variable _request_handler provides access to the calling
    BaseHTTPRequestHandler object that is handling the request on behalf of the
    HTTPServer.
    The handle method needs to be overridden by subclasses.
    """

    def __init__(self, http_request_handler):
        self._request_handler = http_request_handler

    @abc.abstractmethod
    def handle(self):
        pass


class HTTPRequestDispatcher(BaseHTTPRequestHandler):
    """Dispatches HTTP Request to the appropriate handler

    Handlers are externally stored. This class acts as the RequestHandlerClass
    for the HTTPServer.

    Supported HTTP Methods: GET, POST, PUT
    """

    def get_handler(self, method):
        return self.server.handler_registry.get_handler(method, self.path)

    def do_GET(self):
        handler = self.get_handler(HTTPMethod.GET)
        if handler:
            handler(self).handle()

    def do_POST(self):
        handler = self.get_handler(HTTPMethod.POST)
        if handler:
            handler(self).handle()

    def do_PATCH(self):
        handler = self.get_handler(HTTPMethod.PATCH)
        if handler:
            handler(self).handle()


class MultiHandlerSingleThreadHTTPServer(HTTPServer):
    """Create a Basic Single-Threaded HTTP Server where the user can register
    handlers.

    The server can be started sync as well as async. To close the server, you
    must call the shutdown method.
    By default, the HTTP Server has no handlers and acts as a dumb server.
    See register_default_handler to register default handlers to this server.
    See register_handler to register handlers for specific paths to this
    server.
    This server uses a http.HTTPServer which is single-threaded. That means it
    must completely handle a request before it can handle another.
    """

    def __init__(self, host='', port=0):
        """
        Creates the HTTP Server which binds to the host and port passed.

        Args:
            host (string): Defaults to '' or localhost
            port (int): If nothing is passed, defaults to 0, assigns a random
                port.
        """
        if host is None or not isinstance(host, str):
            raise ValueError("Host should be a string!")
        elif port < 0:
            raise ValueError("Port should be non-negative integer")

        super().__init__((host, port), HTTPRequestDispatcher)
        self.handler_registry = HTTPHandlerRegistry()
        self.serving = False
        self.server_thread = None

    def start_serving_sync(self):
        if not self.serving:
            self.serving = True
            self.serve_forever()

    def start_serving_async(self):
        # Create a thread to run the server on with a name containing the
        # server's address
        if not self.serving:
            server_thread_name = "Server-Thread::Address:" + \
                str(self.server_address[0]) + \
                "Port:" + str(self.server_address[1])
            self.server_thread = threading.Thread(
                target=self.start_serving_sync, name=server_thread_name)
            self.server_thread.start()

    def shutdown(self):
        if self.serving:
            super().shutdown()
            self.server_close()
            if self.server_thread:
                self.server_thread.join()
            self.serving = False

    def register_handler(self, method, path, handler):
        """Registers a handler to the server for serving requests with the
        passed method on the passed path.

        Overwrites any handler already attached with the (method, path) to this
        server.

        Args:
            method (HTTPMethod): HTTP verb for the handler
            path (string): Resource path. eg: '/'
            handler (StatelessHTTPHandler): Must implement the handle method
        """
        self.handler_registry.register_request_handler(method, path, handler)

    def register_default_handler(self, method, handler):
        """Registers a default handler for responding to requests on paths for
        which there is no explicitly attached handler.

        Overwrites any handler attached with the method to this server.

        Args:
            method (HTTPMethod): HTTP verb for the handler
            handler (StatelessHTTPHandler): Must implement the handle method
        """
        self.handler_registry.register_default_request_handler(method, handler)

    def deregister_handler(self, method, path):
        self.handler_registry.deregister_request_handler(method, path)

    def deregister_default_handler(self, method):
        self.handler_registry.deregister_default_request_handler(method)

    def __del__(self):
        self.shutdown()

    def __exit__(self, exception_type, exception_value, traceback):
        self.shutdown()

    def __enter__(self):
        return self

import http
import time
import unittest

from omnilib import http as h


class TestHTTPServer(unittest.TestCase):
    class GETStatusOKHandler(h.StatelessHTTPHandler):
        def handle(self):
            self._request_handler.send_response(http.HTTPStatus.OK)
            self._request_handler.end_headers()

    class GETStatusNotFoundHandler(h.StatelessHTTPHandler):
        def handle(self):
            self._request_handler.send_response(http.HTTPStatus.NOT_FOUND)
            self._request_handler.end_headers()

    def start_server_with_handlers(self, handler_registries=[], default_handler_registries=[]):
        server = h.MultiHandlerSingleThreadHTTPServer()
        for registry in handler_registries:
            method, path, handler = registry
            server.register_handler(method, path, handler)
        for registry in default_handler_registries:
            method, handler = registry
            server.register_default_handler(method, handler)
        host, port = server.server_address()
        return (host, port, server)

    def assert_response(self, host, port, method, path, response_code):
        connection = http.client.HTTPConnection(host, port)
        connection.request(method.name, path)
        response = connection.getresponse()
        self.assertEqual(response.status, response_code)
        connection.close()

    def test_server_async(self):
        host, port, server = self.start_server_with_handlers(
            handler_registries=[(h.HTTPMethod.GET, "/", self.GETStatusOKHandler)])
        server.start_serving_async()
        self.assert_response(host, port, h.HTTPMethod.GET,
                             "/", http.HTTPStatus.OK)
        server.shutdown()

    def test_server_multiple_async_calls(self):
        host, port, server = self.start_server_with_handlers(
            handler_registries=[(h.HTTPMethod.GET, "/", self.GETStatusOKHandler)])
        server.start_serving_async()
        server.start_serving_async()
        self.assert_response(host, port, h.HTTPMethod.GET,
                             "/", http.HTTPStatus.OK)
        server.start_serving_async()
        server.start_serving_async()
        self.assert_response(host, port, h.HTTPMethod.GET,
                             "/", http.HTTPStatus.OK)
        server.shutdown()

    def test_server_multiple_shutdown_calls(self):
        host, port, server = self.start_server_with_handlers(
            handler_registries=[(h.HTTPMethod.GET, "/", self.GETStatusOKHandler)])
        server.start_serving_async()
        self.assert_response(host, port, h.HTTPMethod.GET,
                             "/", http.HTTPStatus.OK)
        server.shutdown()
        server.shutdown()

    def test_register_multiple_handlers(self):
        host, port, server = self.start_server_with_handlers(handler_registries=[(
            h.HTTPMethod.GET, "/", self.GETStatusOKHandler), (h.HTTPMethod.GET, "/another_path", self.GETStatusOKHandler)])
        server.start_serving_async()
        self.assert_response(host, port, h.HTTPMethod.GET,
                             "/", http.HTTPStatus.OK)
        self.assert_response(host, port, h.HTTPMethod.GET,
                             "/another_path", http.HTTPStatus.OK)
        server.shutdown()

    def test_server_register_default_handler(self):
        host, port, server = self.start_server_with_handlers(
            default_handler_registries=[(h.HTTPMethod.GET, self.GETStatusNotFoundHandler)])
        server.start_serving_async()
        self.assert_response(host, port, h.HTTPMethod.GET,
                             "/", http.HTTPStatus.NOT_FOUND)
        server.shutdown()

    def test_server_register_multiple_and_default_handlers(self):
        host, port, server = self.start_server_with_handlers(handler_registries=[(h.HTTPMethod.GET, "/", self.GETStatusOKHandler), (
            h.HTTPMethod.GET, "/handled_path", self.GETStatusOKHandler)], default_handler_registries=[(h.HTTPMethod.GET, self.GETStatusNotFoundHandler)])
        server.start_serving_async()
        self.assert_response(host, port, h.HTTPMethod.GET,
                             "/", http.HTTPStatus.OK)
        self.assert_response(host, port, h.HTTPMethod.GET,
                             "/handled_path", http.HTTPStatus.OK)
        self.assert_response(host, port, h.HTTPMethod.GET,
                             "/any_other_path", http.HTTPStatus.NOT_FOUND)
        server.shutdown()

    def test_server_deregister_handlers(self):
        host, port, server = self.start_server_with_handlers(handler_registries=[(
            h.HTTPMethod.GET, "/", self.GETStatusOKHandler)], default_handler_registries=[(h.HTTPMethod.GET, self.GETStatusNotFoundHandler)])
        with server:
            server.start_serving_async()
            self.assert_response(
                host, port, h.HTTPMethod.GET, "/", http.HTTPStatus.OK)
            self.assert_response(host, port, h.HTTPMethod.GET,
                                 "/any_other_path", http.HTTPStatus.NOT_FOUND)
            server.deregister_handler(h.HTTPMethod.GET, "/")
            self.assert_response(host, port, h.HTTPMethod.GET,
                                 "/", http.HTTPStatus.NOT_FOUND)
            server.deregister_default_handler(h.HTTPMethod.GET)
            with self.assertRaises(http.client.BadStatusLine):
                self.assert_response(
                    host, port, h.HTTPMethod.GET, "/", http.HTTPStatus.NOT_FOUND)

    def test_server_with(self):
        with h.MultiHandlerSingleThreadHTTPServer() as server:
            host, port = server.server_address()
            server.register_handler(
                h.HTTPMethod.GET, "/", self.GETStatusOKHandler)
            server.start_serving_async()
            self.assert_response(
                host, port, h.HTTPMethod.GET, "/", http.HTTPStatus.OK)


if __name__ == '__main__':
    unittest.main()

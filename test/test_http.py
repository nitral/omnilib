import http
import time
import unittest

import jsonpickle
from omnilib import http as h
from omnilib import util


class TestProbeResource(unittest.TestCase):
    def test_prober(self):
        prober_path = 'prober'
        prober_desc = 'Test Probe Resource!'
        prober = h.ProbeResource(prober_path, desc=prober_desc)

        self.assertEqual(prober.get_path(), prober_path)
        self.assertEqual(prober.get_desc(), prober_desc)

    def test_add_probe(self):
        prober = h.ProbeResource('prober')

        int_var = util.MutableVariable(123)
        int_var_desc = 'Integer Variable'

        prober.add_probe('int_var', int_var, desc=int_var_desc)

        self.assertEqual(prober.get_probe_value('int_var'), int_var)
        self.assertEqual(prober.get_probe_desc('int_var'), int_var_desc)

        with self.assertRaises(ValueError):
            prober.add_probe('int_var', 123)

    def test_set_probe_value(self):
        prober = h.ProbeResource('prober')

        int_var = util.MutableVariable(123)
        int_var_desc = 'Integer Variable'

        prober.add_probe('int_var', int_var, desc=int_var_desc)

        new_int_var = util.MutableVariable(456)

        prober.set_probe_value('int_var', new_int_var)

        self.assertEqual(prober.get_probe_value('int_var'), new_int_var)

        with self.assertRaises(ValueError):
            prober.set_probe_value('int_var', 123)

    def test_getters(self):
        prober = h.ProbeResource('prober')

        int_var = util.MutableVariable(123)
        int_var_desc = 'Test Integer Variable'
        bool_var = util.MutableVariable(False)
        bool_var_desc = 'Test Boolean Variable'

        prober.add_probe('int_var', int_var, desc=int_var_desc)
        prober.add_probe('bool_var', bool_var, desc=bool_var_desc)

        self.assertEqual(sorted(prober.get_probe_labels()),
                         sorted(['int_var', 'bool_var']))
        self.assertDictEqual(prober.get_probe_descriptions(), {
                             'int_var': int_var_desc, 'bool_var': bool_var_desc})
        self.assertDictEqual(prober.get_probe_values(), {
                             'int_var': int_var, 'bool_var': bool_var})


class TestProbeResourceHandlers(unittest.TestCase):
    def test_patch_handler(self):
        with h.MultiHandlerSingleThreadHTTPServer() as server:
            host, port = server.server_address()
            print(host, port)

            # Create Variables to export to server
            int_var = util.MutableVariable(123)
            bool_var = util.MutableVariable(True)
            string_var = util.MutableVariable('Test Case')
            list_var = util.MutableVariable([1, 2, 3])
            dict_var = util.MutableVariable(
                {'key1': 'value1', 'key2': 'value2'})

            # Create a prober on path /probes/vars
            prober = h.ProbeResource('/vars')
            prober.add_probe('int_var', int_var)
            prober.add_probe('bool_var', bool_var)
            prober.add_probe('string_var', string_var)
            prober.add_probe('list_var', list_var)
            prober.add_probe('dict_var', dict_var)

            # Export prober to the server
            h.export_probe_resource_to_server(server, prober)

            # Start serving
            server.start_serving_async()

            # Send PUT request to /probes/vars
            connection = http.client.HTTPConnection(host, port)
            connection.request(h.HTTPMethod.PATCH.name, "/probes/vars",
                               body="{\"bool_var\":{\"_value\":false,\"py\/object\":\"omnilib.util.container.MutableVariable\"},\"dict_var\":{\"_value\":{\"key3\":\"value3\",\"key4\":\"value4\"},\"py\/object\":\"omnilib.util.container.MutableVariable\"},\"int_var\":{\"_value\":456,\"py\/object\":\"omnilib.util.container.MutableVariable\"},\"list_var\":{\"_value\":[4,5,6],\"py\/object\":\"omnilib.util.container.MutableVariable\"},\"string_var\":{\"_value\":\"Case Test\",\"py\/object\":\"omnilib.util.container.MutableVariable\"}}")
            response = connection.getresponse()
            self.assertEqual(response.status, http.HTTPStatus.OK)

            # Validate response
            self.assertEqual(
                prober.get_probe_value('int_var'), 456)
            self.assertEqual(
                prober.get_probe_value('bool_var'), False)
            self.assertEqual(prober.get_probe_value(
                'string_var'), string_var)
            self.assertEqual(
                prober.get_probe_value('list_var'), [4, 5, 6])
            self.assertEqual(
                prober.get_probe_value('dict_var'), {'key3': 'value3', 'key4': 'value4'})

            # Close connection
            connection.close()

    def test_get_handler(self):
        with h.MultiHandlerSingleThreadHTTPServer() as server:
            host, port = server.server_address()

            # Create Variables to export to server
            mutvar_var = util.MutableVariable(util.MutableVariable(123))
            int_var = util.MutableVariable(32416190071)
            bool_var = util.MutableVariable(True)
            string_var = util.MutableVariable(
                '9bd3aaa3-cc7c-4aac-a6df-2dc5ae1e68a2')
            list_var = util.MutableVariable(
                [15487039, '2c7e5965-e6d6-412c-93f0-b652687ccd12', 105653])
            dict_var = util.MutableVariable(
                {'key1': '08bc2431-8ed6-4bcf-a3a9-79bef3e00c4d', 'key2': '0999f3ab-7521-446d-94ce-f659dea8183a'})

            # Create a prober on path /probers/vars
            prober = h.ProbeResource(
                '/vars', desc='Test Probe Resource Description')
            prober.add_probe('mutvar_var', mutvar_var)
            prober.add_probe('int_var', int_var)
            prober.add_probe('bool_var', bool_var)
            prober.add_probe('string_var', string_var)
            prober.add_probe('list_var', list_var)
            prober.add_probe('dict_var', dict_var)

            # Export prober to the server
            h.export_probe_resource_to_server(server, prober)

            # Start serving
            server.start_serving_async()

            # Read GET response at /probers/vars
            connection = http.client.HTTPConnection(host, port)
            connection.request(h.HTTPMethod.GET.name, "/probes/vars")
            response = connection.getresponse()
            self.assertEqual(response.status, http.HTTPStatus.OK)
            content_length = int(response.getheader('Content-Length'))
            response_string = response.read(content_length)

            # Validate response
            self.assertTrue(b'32416190071' in response_string)
            self.assertTrue(
                b'9bd3aaa3-cc7c-4aac-a6df-2dc5ae1e68a2' in response_string)
            self.assertTrue(b'15487039' in response_string)
            self.assertTrue(
                b'2c7e5965-e6d6-412c-93f0-b652687ccd12' in response_string)
            self.assertTrue(b'105653' in response_string)
            self.assertTrue(
                b'08bc2431-8ed6-4bcf-a3a9-79bef3e00c4d' in response_string)
            self.assertTrue(
                b'0999f3ab-7521-446d-94ce-f659dea8183a' in response_string)

            # Close connection
            connection.close()


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

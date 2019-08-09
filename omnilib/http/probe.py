import http
import inspect
import os

import jsonpickle
import jsonpickle.ext.numpy as jsonpickle_numpy
from mako.template import Template

from ..util import MutableVariable, Singleton
from .server import HTTPMethod, StatelessHTTPHandler

_probe_root_path = "/probes"
jsonpickle_numpy.register_handlers()


def _get_probe_absolute_path(resource):
    return _probe_root_path + '/' + resource.get_path()


def export_probe_resource_to_server(server, probe_resource):
    """Exports the Probe Resource to the given server for editing.

    Registers a GET Handler at /probes/{probe_resource.path}
    Registers a PATCH Handler at /probes/{probe_resource.path}

    The GET Handler is served by a HTML page that allows for easy viewing and
    editing of the Probe Resource.
    Overwrites any existing Probe Resource at the same path on this server.
    """
    ProbeResourceHandlerRegistry().register_probe_resource(
        server.server_address(), probe_resource)
    probe_path = _get_probe_absolute_path(probe_resource)
    server.register_handler(HTTPMethod.GET, probe_path,
                            ProbeResourceGETHandler)
    server.register_handler(HTTPMethod.PATCH, probe_path,
                            ProbeResourcePATCHHandler)


class ProbeResourceGETHandler(StatelessHTTPHandler):
    def handle(self):
        probe_resource = ProbeResourceHandlerRegistry().get_probe_resource(
            self._request_handler.server.server_address, self._request_handler.path)
        html_template = Template(filename=os.path.join(os.path.dirname(
            inspect.getfile(ProbeResourceGETHandler)), 'data', 'probes', 'prober.html'))
        html_response = html_template.render(prober_path=probe_resource.get_path(), prober_desc=probe_resource.get_desc(), prober_dict=jsonpickle.encode(
            probe_resource.get_probe_values()), prober_desc_dict=jsonpickle.encode(probe_resource.get_probe_descriptions()))
        self._request_handler.send_response(http.HTTPStatus.OK)
        self._request_handler.send_header('Content-Length', len(html_response))
        self._request_handler.end_headers()
        self._request_handler.wfile.write(bytes(html_response, 'utf-8'))


class ProbeResourcePATCHHandler(StatelessHTTPHandler):
    def handle(self):
        content_length = int(self._request_handler.headers['Content-Length'])
        response_string = self._request_handler.rfile.read(content_length)
        probes = jsonpickle.decode(response_string)
        probe_resource = ProbeResourceHandlerRegistry().get_probe_resource(
            self._request_handler.server.server_address, self._request_handler.path)

        # Check if response is valid
        for key, value in probes.items():
            if not isinstance(value, MutableVariable):
                self._request_handler.send_response(
                    http.HTTPStatus.BAD_REQUEST)
                self._request_handler.end_headers()
                return

        # Set received value
        for key, value in probes.items():
            probe_resource.get_probe_value(key).set_value(value.get_value())

        self._request_handler.send_response(http.HTTPStatus.OK)
        self._request_handler.end_headers()


class ProbeResourceHandlerRegistry(metaclass=Singleton):
    """Global Singleton Handler Registry for all Omnilib Probe Resources

    Maintains a registry mapping of Probe Resource Handlers mapped to their
    corresponding server addresses.
    """

    def __init__(self):
        self.registry = {}

    def register_probe_resource(self, server_address, resource):
        if server_address not in self.registry:
            self.registry[server_address] = {}
        self.registry[server_address][_get_probe_absolute_path(
            resource)] = resource

    def get_probe_resource(self, server_address, path):
        return self.registry.get(server_address, {}).get(path, None)


class ProbeResource(object):
    """A Probe Resource encapsulates a group of probes defined as labelled
    Mutable Variables.

    A probe resource is initialized with a path that acts as a child path to
    the /probes root.
    A probe must have a label and can have an optional description. All probe
    values must be Mutable Variables.
    """

    def __init__(self, path, desc=''):
        self.path = path.strip('/')
        self.desc = desc
        self.probe_dict = {}
        self.probe_desc_dict = {}

    def add_probe(self, label, mutable_variable, desc=''):
        """Adds a labelled probe to the Probe Resource. Overwrites any
        preexisting probe with the same label.

        Args:
            label (str): Primary identifier for the probe
            mutable_variable (util.MutableVariable): The probe value.
            desc (str): Optional description for the probe

        Raises:
            ValueError: If passed value is not a MutableVariable
        """
        if not isinstance(mutable_variable, MutableVariable):
            raise ValueError("Passed probe should be of type MutableVariable!")
        self.probe_dict[label] = mutable_variable
        self.probe_desc_dict[label] = desc

    def set_probe_value(self, label, value):
        """Sets the MutableVariable value of a probe with the given label.

        Raises:
            ValueError: If the passed value is not a MutableVariable
        """
        if not isinstance(value, MutableVariable):
            raise ValueError("Passed value should be of type MutableVariable!")
        if label in self.probe_dict:
            self.probe_dict[label] = value

    def get_probe_value(self, label):
        """Gets the probe MutableVariable value with the label. Returns None if
        the probe does not exist.
        """
        if label in self.probe_dict:
            return self.probe_dict[label]

    def get_probe_desc(self, label):
        if label in self.probe_desc_dict:
            return self.probe_desc_dict[label]

    def get_probes(self):
        """Returns a tuple containing the probe values and the descriptions
        dictionaries.
        The keys of the dictionaries are the labels of the probes
        """
        return (self.probe_dict, self.probe_desc_dict)

    def get_probe_values(self):
        return self.probe_dict

    def get_probe_labels(self):
        return list(self.probe_dict.keys())

    def get_probe_descriptions(self):
        return self.probe_desc_dict

    def get_path(self):
        return self.path

    def get_desc(self):
        return self.desc

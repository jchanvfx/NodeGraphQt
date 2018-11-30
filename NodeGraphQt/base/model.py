#!/usr/bin/python
import json
from collections import defaultdict

from NodeGraphQt.constants import (NODE_PROP,
                                   NODE_PROP_QLINEEDIT,
                                   NODE_PROP_QCHECKBOX,
                                   NODE_PROP_COLORPICKER)


class PortModel(object):

    def __init__(self, node):
        self.node = node
        self.type = ''
        self.name = 'port'
        self.display_name = True
        self.multi_connection = False
        self.connected_ports = defaultdict(list)

    def __repr__(self):
        return '{}(\'{}\')'.format(self.__class__.__name__, self.name)

    @property
    def to_dict(self):
        """
        serialize model information to a dictionary.

        Returns:
            dict: node port dictionary eg.
                {
                    'type': 'in',
                    'name': 'port',
                    'display_name': True,
                    'multi_connection': False,
                    'connected_ports': {<node_id>: [<port_name>, <port_name>]}
                }
        """
        props = self.__dict__.copy()
        props.pop('node')
        props['connected_ports'] = dict(props.pop('connected_ports'))
        return props


class NodeModel(object):

    def __init__(self):
        self.type = None
        self.id = hex(id(self))
        self.icon = None
        self.name = 'node'
        self.color = (13, 18, 23, 255)
        self.border_color = (74, 84, 85, 255)
        self.text_color = (255, 255, 255, 180)
        self.disabled = False
        self.selected = False
        self.width = 100.0
        self.height = 80.0
        self.pos = (0.0, 0.0)
        self.inputs = {}
        self.outputs = {}
        self._custom_prop = {}

        # node graph model set at node added time.
        self._graph_model = None

        # store the property attributes.
        # (deleted when node is added to the graph)
        self._TEMP_property_attrs = {}
        # temp store the property widget types.
        # (deleted when node is added to the graph)
        self._TEMP_property_widget_types = {
            'type': NODE_PROP,
            'id': NODE_PROP,
            'icon': NODE_PROP,
            'name': NODE_PROP_QLINEEDIT,
            'color': NODE_PROP_COLORPICKER,
            'border_color': NODE_PROP,
            'text_color': NODE_PROP,
            'disabled': NODE_PROP_QCHECKBOX,
            'selected': NODE_PROP,
            'width': NODE_PROP,
            'height': NODE_PROP,
            'pos': NODE_PROP,
            'inputs': NODE_PROP,
            'outputs': NODE_PROP,
        }

    def add_property(self, name, value, items=None, range=None, widget_type=NODE_PROP):
        """
        add custom property.

        Args:
            name (str): name of the property.
            value (object): data.
            items (list[str]): items used by widget type NODE_PROP_QCOMBO.
            range (tuple)): min, max values used by NODE_PROP_SLIDER.
            widget_type (int): widget type flag.
        """
        if name in self.properties.keys():
            raise AssertionError('"{}" reserved for defaults.'.format(name))
        if name in self._custom_prop.keys():
            raise AssertionError('"{}" property already exists.'.format(name))

        self._custom_prop[name] = value

        if self._graph_model is None:
            self._TEMP_property_widget_types[name] = widget_type
            self._TEMP_property_attrs[name] = {}
            if items:
                self._TEMP_property_attrs[name]['items'] = items
            if range:
                self._TEMP_property_attrs[name]['range'] = range
        else:
            attrs = {self.type: {name: {'widget_type': widget_type}}}
            if items:
                attrs[self.type][name]['items'] = items
            if range:
                attrs[self.type][name]['range'] = range
            self._graph_model.node_property_attrs.update(attrs)

    def set_property(self, name, value):
        if name in self.properties.keys():
            setattr(self, name, value)
        elif name in self._custom_prop.keys():
            self._custom_prop[name] = value
        else:
            raise KeyError('No property "{}"'.format(name))

    def get_property(self, name):
        if name in self.properties.keys():
            return self.properties[name]
        return self._custom_prop.get(name)

    def get_widget_type(self, name):
        graph = self._graph_model
        if graph is None:
            return self._TEMP_property_widget_types.get(name)
        return graph.node_property_attrs[self.type][name]['widget_type']

    @property
    def properties(self):
        """
        return all default node properties.

        Returns:
            dict: default node properties.
        """
        props = self.__dict__.copy()
        props.pop('_custom_prop')
        return props

    @property
    def custom_properties(self):
        """
        return all custom properties specified by the user.

        Returns:
            dict: user defined properties.
        """
        return self._custom_prop

    @property
    def to_dict(self):
        """
        serialize model information to a dictionary.

        Returns:
            dict: node id as the key and properties as the values eg.
                {'0x106cf75a8': {
                    'name': 'foo node',
                    'color': (48, 58, 69, 255),
                    'border_color': (85, 100, 100, 255),
                    'text_color': (255, 255, 255, 180),
                    'type': 'com.chantasticvfx.FooNode',
                    'selected': False,
                    'disabled': False,
                    'inputs': {
                        <port_name>: {<node_id>: [<port_name>, <port_name>]}},
                    'outputs': {
                        <port_name>: {<node_id>: [<port_name>, <port_name>]}},
                    'width': 0.0,
                    'height: 0.0,
                    'pos': (0.0, 0.0),
                    'custom': {},
                    }
                }
        """
        node_dict = self.__dict__.copy()
        node_id = node_dict.pop('id')

        inputs = {}
        outputs = {}
        for name, model in node_dict.pop('inputs').items():
            connected_ports = model.to_dict['connected_ports']
            if connected_ports:
                inputs[name] = connected_ports
        for name, model in node_dict.pop('outputs').items():
            connected_ports = model.to_dict['connected_ports']
            if connected_ports:
                outputs[name] = connected_ports
        if inputs:
            node_dict['inputs'] = inputs
        if outputs:
            node_dict['outputs'] = outputs

        custom_props = node_dict.pop('_custom_prop', {})
        if custom_props:
            node_dict['custom'] = custom_props

        exclude = ['_graph_model',
                   '_TEMP_property_attrs',
                   '_TEMP_property_widget_types']
        [node_dict.pop(i) for i in exclude if i in node_dict.keys()]

        return {node_id: node_dict}

    @property
    def serial(self):
        """
        Serialize model information to a string.

        Returns:
            str: serialized JSON string.
        """
        model_dict = self.to_dict
        return json.dumps(model_dict)


class NodeGraphModel(object):

    def __init__(self):
        self.nodes = {}
        self.session = ''
        self.acyclic = True

        # store common node property attrs.
        # eg.
        # {'nodeGraphQt.nodes.FooNode': {
        #     'my_property':{
        #         'widget_type': 0,
        #         'items': ['foo', 'bar', 'test'],
        #         'range': (0, 100)
        #         }
        #     }
        # }
        self.node_property_attrs = {}


if __name__ == '__main__':
    p = PortModel(None)
    # print(p.to_dict)

    n = NodeModel()
    n.inputs[p.name] = p
    n.add_property('foo', 'bar')
    # print(n.properties)
    for k, v in n.to_dict[n.id].items():
        print(k, v)

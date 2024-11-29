#!/usr/bin/python
import json
from collections import defaultdict

from NodeGraphQt.constants import (
    LayoutDirectionEnum,
    NodePropWidgetEnum,
    PipeLayoutEnum
)
from NodeGraphQt.errors import NodePropertyError


class PortModel(object):
    """
    Data dump for a port object.
    """

    def __init__(self, node):
        self.node = node
        self.type_ = ''
        self.name = 'port'
        self.display_name = True
        self.multi_connection = False
        self.visible = True
        self.locked = False
        self.connected_ports = defaultdict(list)

    def __repr__(self):
        return '<{}(\'{}\') object at {}>'.format(
            self.__class__.__name__, self.name, hex(id(self)))

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
                    'visible': True,
                    'locked': False,
                    'connected_ports': {<node_id>: [<port_name>, <port_name>]}
                }
        """
        props = self.__dict__.copy()
        props.pop('node')
        props['connected_ports'] = dict(props.pop('connected_ports'))
        return props


class NodeModel(object):
    """
    Data dump for a node object.
    """

    def __init__(self):
        self.type_ = None
        self.id = hex(id(self))
        self.icon = None
        self.name = 'node'
        self.color = (13, 18, 23, 255)
        self.border_color = (74, 84, 85, 255)
        self.text_color = (255, 255, 255, 180)
        self.disabled = False
        self.selected = False
        self.visible = True
        self.width = 100.0
        self.height = 80.0
        self.pos = [0.0, 0.0]
        self.layout_direction = LayoutDirectionEnum.HORIZONTAL.value

        # BaseNode attrs.
        self.inputs = {}
        self.outputs = {}
        self.port_deletion_allowed = False

        # GroupNode attrs.
        self.subgraph_session = {}

        # Custom
        self._custom_prop = {}

        # node graph model set at node added time.
        self._graph_model = None

        # store the property attributes.
        # (deleted when node is added to the graph)
        self._TEMP_property_attrs = {}

        # temp store the property widget types.
        # (deleted when node is added to the graph)
        self._TEMP_property_widget_types = {
            'type_': NodePropWidgetEnum.QLABEL.value,
            'id': NodePropWidgetEnum.QLABEL.value,
            'icon': NodePropWidgetEnum.HIDDEN.value,
            'name': NodePropWidgetEnum.QLINE_EDIT.value,
            'color': NodePropWidgetEnum.COLOR_PICKER.value,
            'border_color': NodePropWidgetEnum.COLOR_PICKER.value,
            'text_color': NodePropWidgetEnum.COLOR_PICKER.value,
            'disabled': NodePropWidgetEnum.QCHECK_BOX.value,
            'selected': NodePropWidgetEnum.HIDDEN.value,
            'width': NodePropWidgetEnum.HIDDEN.value,
            'height': NodePropWidgetEnum.HIDDEN.value,
            'pos': NodePropWidgetEnum.HIDDEN.value,
            'layout_direction': NodePropWidgetEnum.HIDDEN.value,
            'inputs': NodePropWidgetEnum.HIDDEN.value,
            'outputs': NodePropWidgetEnum.HIDDEN.value,
        }

        # temp store connection constrains.
        # (deleted when node is added to the graph)
        self._TEMP_accept_connection_types = {}
        self._TEMP_reject_connection_types = {}

    def __repr__(self):
        return '<{}(\'{}\') object at {}>'.format(
            self.__class__.__name__, self.name, self.id)

    def add_property(self, name, value, items=None, range=None,
                     widget_type=None, widget_tooltip=None, tab=None):
        """
        add custom property or raises an error if the property name is already
        taken.

        Args:
            name (str): name of the property.
            value (object): data.
            items (list[str]): items used by widget type NODE_PROP_QCOMBO.
            range (tuple): min, max values used by NODE_PROP_SLIDER.
            widget_type (int): widget type flag.
            widget_tooltip (str): custom tooltip for the property widget.
            tab (str): widget tab name.
        """
        widget_type = widget_type or NodePropWidgetEnum.HIDDEN.value
        tab = tab or 'Properties'

        if name in self.properties.keys():
            raise NodePropertyError(
                '"{}" reserved for default property.'.format(name))
        if name in self._custom_prop.keys():
            raise NodePropertyError(
                '"{}" property already exists.'.format(name))

        self._custom_prop[name] = value

        if self._graph_model is None:
            self._TEMP_property_widget_types[name] = widget_type
            self._TEMP_property_attrs[name] = {'tab': tab}
            if items:
                self._TEMP_property_attrs[name]['items'] = items
            if range:
                self._TEMP_property_attrs[name]['range'] = range
            if widget_tooltip:
                self._TEMP_property_attrs[name]['tooltip'] = widget_tooltip

        else:
            attrs = {
                self.type_: {
                    name: {
                        'widget_type': widget_type,
                        'tab': tab
                    }
                }
            }
            if items:
                attrs[self.type_][name]['items'] = items
            if range:
                attrs[self.type_][name]['range'] = range
            if widget_tooltip:
                attrs[self.type_][name]['tooltip'] = widget_tooltip
            self._graph_model.set_node_common_properties(attrs)

    def set_property(self, name, value):
        """
        Args:
            name (str): property name.
            value (object): property value.
        """
        if name in self.properties.keys():
            setattr(self, name, value)
        elif name in self._custom_prop.keys():
            self._custom_prop[name] = value
        else:
            raise NodePropertyError('No property "{}"'.format(name))

    def get_property(self, name):
        """
        Args:
            name (str): property name.

        Returns:
            object: property value.
        """
        if name in self.properties.keys():
            return self.properties[name]
        return self._custom_prop.get(name)

    def is_custom_property(self, name):
        """
        Args:
            name (str): property name.

        Returns:
            bool: true if custom property.
        """
        return name in self._custom_prop

    def get_widget_type(self, name):
        """
        Args:
            name (str): property name.

        Returns:
            int: node property widget type.
        """
        model = self._graph_model
        if model is None:
            return self._TEMP_property_widget_types.get(name)
        return model.get_node_common_properties(self.type_)[name]['widget_type']

    def get_tab_name(self, name):
        """
        Args:
            name (str): property name.

        Returns:
            str: name of the tab for the properties bin.
        """
        model = self._graph_model
        if model is None:
            attrs = self._TEMP_property_attrs.get(name)
            if attrs:
                return attrs[name].get('tab')
            return
        return model.get_node_common_properties(self.type_)[name]['tab']

    def add_port_accept_connection_type(
            self,
            port_name, port_type, node_type,
            accept_pname, accept_ptype, accept_ntype
    ):
        """
        Convenience function for adding to the "accept_connection_types" dict.
        If the node graph model is unavailable, yet then we store it to a
        temp var that gets deleted.

        Args:
            port_name (str): current port name.
            port_type (str): current port type.
            node_type (str): current port node type.
            accept_pname (str):port name to accept.
            accept_ptype (str): port type accept.
            accept_ntype (str):port node type to accept.
        """
        model = self._graph_model
        if model:
            model.add_port_accept_connection_type(
                port_name, port_type, node_type,
                accept_pname, accept_ptype, accept_ntype
            )
            return

        connection_data = self._TEMP_accept_connection_types
        keys = [node_type, port_type, port_name, accept_ntype]
        for key in keys:
            if key not in connection_data.keys():
                connection_data[key] = {}
            connection_data = connection_data[key]

        if accept_ptype not in connection_data:
            connection_data[accept_ptype] = set([accept_pname])
        else:
            connection_data[accept_ptype].add(accept_pname)

    def add_port_reject_connection_type(
        self,
        port_name, port_type, node_type,
        reject_pname, reject_ptype, reject_ntype
    ):
        """
        Convenience function for adding to the "reject_connection_types" dict.
        If the node graph model is unavailable yet then we store it to a
        temp var that gets deleted.

        Args:
            port_name (str): current port name.
            port_type (str): current port type.
            node_type (str): current port node type.
            reject_pname:
            reject_ptype:
            reject_ntype:

        Returns:

        """
        model = self._graph_model
        if model:
            model.add_port_reject_connection_type(
                port_name, port_type, node_type,
                reject_pname, reject_ptype, reject_ntype
            )
            return

        connection_data = self._TEMP_reject_connection_types
        keys = [node_type, port_type, port_name, reject_ntype]
        for key in keys:
            if key not in connection_data.keys():
                connection_data[key] = {}
            connection_data = connection_data[key]

        if reject_ptype not in connection_data:
            connection_data[reject_ptype] = set([reject_pname])
        else:
            connection_data[reject_ptype].add(reject_pname)

    @property
    def properties(self):
        """
        return all default node properties.

        Returns:
            dict: default node properties.
        """
        props = self.__dict__.copy()
        exclude = ['_custom_prop',
                   '_graph_model',
                   '_TEMP_property_attrs',
                   '_TEMP_property_widget_types']
        [props.pop(i) for i in exclude if i in props.keys()]
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
                    'type_': 'io.github.jchanvfx.FooNode',
                    'selected': False,
                    'disabled': False,
                    'visible': True,
                    'width': 0.0,
                    'height: 0.0,
                    'pos': (0.0, 0.0),
                    'layout_direction': 0,
                    'custom': {},
                    'inputs': {
                        <port_name>: {<node_id>: [<port_name>, <port_name>]}
                    },
                    'outputs': {
                        <port_name>: {<node_id>: [<port_name>, <port_name>]}
                    },
                    'input_ports': [<port_name>, <port_name>],
                    'output_ports': [<port_name>, <port_name>],
                    },
                    subgraph_session: <sub graph session data>
                }
        """
        node_dict = self.__dict__.copy()
        node_id = node_dict.pop('id')

        inputs = {}
        outputs = {}
        input_ports = []
        output_ports = []
        for name, model in node_dict.pop('inputs').items():
            if self.port_deletion_allowed:
                input_ports.append({
                    'name': name,
                    'multi_connection': model.multi_connection,
                    'display_name': model.display_name,
                })
            connected_ports = model.to_dict['connected_ports']
            if connected_ports:
                inputs[name] = connected_ports
        for name, model in node_dict.pop('outputs').items():
            if self.port_deletion_allowed:
                output_ports.append({
                    'name': name,
                    'multi_connection': model.multi_connection,
                    'display_name': model.display_name,
                })
            connected_ports = model.to_dict['connected_ports']
            if connected_ports:
                outputs[name] = connected_ports
        if inputs:
            node_dict['inputs'] = inputs
        if outputs:
            node_dict['outputs'] = outputs

        if self.port_deletion_allowed:
            node_dict['input_ports'] = input_ports
            node_dict['output_ports'] = output_ports

        if self.subgraph_session:
            node_dict['subgraph_session'] = self.subgraph_session

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
    """
    Data dump for a node graph.
    """

    def __init__(self):
        self.__common_node_props = {}

        self.accept_connection_types = {}
        self.reject_connection_types = {}

        self.nodes = {}
        self.session = ''
        self.acyclic = True
        self.pipe_collision = False
        self.pipe_slicing = True
        self.pipe_style = PipeLayoutEnum.CURVED.value
        self.layout_direction = LayoutDirectionEnum.HORIZONTAL.value

    def common_properties(self):
        """
        Return all common node properties.

        Returns:
            dict: common node properties.
                eg.
                    {'nodeGraphQt.nodes.FooNode': {
                        'my_property': {
                            'widget_type': 0,
                            'tab': 'Properties',
                            'items': ['foo', 'bar', 'test'],
                            'range': (0, 100)
                            }
                        }
                    }
        """
        return self.__common_node_props

    def set_node_common_properties(self, attrs):
        """
        Store common node properties.

        Args:
            attrs (dict): common node properties.
                eg.
                    {'nodeGraphQt.nodes.FooNode': {
                        'my_property': {
                            'widget_type': 0,
                            'tab': 'Properties',
                            'items': ['foo', 'bar', 'test'],
                            'range': (0, 100)
                            }
                        }
                    }
        """
        for node_type in attrs.keys():
            node_props = attrs[node_type]

            if node_type not in self.__common_node_props.keys():
                self.__common_node_props[node_type] = node_props
                continue

            for prop_name, prop_attrs in node_props.items():
                common_props = self.__common_node_props[node_type]
                if prop_name not in common_props.keys():
                    common_props[prop_name] = prop_attrs
                    continue
                common_props[prop_name].update(prop_attrs)

    def get_node_common_properties(self, node_type):
        """
        Return all the common properties for a registered node.

        Args:
            node_type (str): node type.

        Returns:
            dict: node common properties.
        """
        return self.__common_node_props.get(node_type)

    def add_port_accept_connection_type(
            self,
            port_name, port_type, node_type,
            accept_pname, accept_ptype, accept_ntype
    ):
        """
        Convenience function for adding to the "accept_connection_types" dict.

        Args:
            port_name (str): current port name.
            port_type (str): current port type.
            node_type (str): current port node type.
            accept_pname (str):port name to accept.
            accept_ptype (str): port type accept.
            accept_ntype (str):port node type to accept.
        """
        connection_data = self.accept_connection_types
        keys = [node_type, port_type, port_name, accept_ntype]
        for key in keys:
            if key not in connection_data.keys():
                connection_data[key] = {}
            connection_data = connection_data[key]

        if accept_ptype not in connection_data:
            connection_data[accept_ptype] = set([accept_pname])
        else:
            # ensure data remains a set instead of list after json de-serialize
            connection_data[accept_ptype] = set(connection_data[accept_ptype]) | {accept_pname}

    def port_accept_connection_types(self, node_type, port_type, port_name):
        """
        Convenience function for getting the accepted port types from the
        "accept_connection_types" dict.

        Args:
            node_type (str):
            port_type (str):
            port_name (str):

        Returns:
            dict: {<node_type>: {<port_type>: [<port_name>]}}
        """
        data = self.accept_connection_types.get(node_type) or {}
        accepted_types = data.get(port_type) or {}
        return accepted_types.get(port_name) or {}

    def add_port_reject_connection_type(
            self,
            port_name, port_type, node_type,
            reject_pname, reject_ptype, reject_ntype
    ):
        """
        Convenience function for adding to the "reject_connection_types" dict.

        Args:
            port_name (str): current port name.
            port_type (str): current port type.
            node_type (str): current port node type.
            reject_pname (str): port name to reject.
            reject_ptype (str): port type to reject.
            reject_ntype (str): port node type to reject.
        """
        connection_data = self.reject_connection_types
        keys = [node_type, port_type, port_name, reject_ntype]
        for key in keys:
            if key not in connection_data.keys():
                connection_data[key] = {}
            connection_data = connection_data[key]

        if reject_ptype not in connection_data:
            connection_data[reject_ptype] = set([reject_pname])
        else:
            # ensure data remains a set instead of list after json de-serialize
            connection_data[reject_ptype] = set(connection_data[reject_ptype]) | {reject_pname}

    def port_reject_connection_types(self, node_type, port_type, port_name):
        """
        Convenience function for getting the accepted port types from the
        "reject_connection_types" dict.

        Args:
            node_type (str):
            port_type (str):
            port_name (str):

        Returns:
            dict: {<node_type>: {<port_type>: [<port_name>]}}
        """
        data = self.reject_connection_types.get(node_type) or {}
        rejected_types = data.get(port_type) or {}
        return rejected_types.get(port_name) or {}


if __name__ == '__main__':
    p = PortModel(None)
    # print(p.to_dict)

    n = NodeModel()
    n.inputs[p.name] = p
    n.add_property('foo', 'bar')

    print('-'*100)
    print('property keys\n')
    print(list(n.properties.keys()))
    print('-'*100)
    print('to_dict\n')
    for k, v in n.to_dict[n.id].items():
        print(k, v)

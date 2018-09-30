#!/usr/bin/python
from NodeGraphQt.base.commands import PropertyChangedCmd
from NodeGraphQt.base.model import NodeModel
from NodeGraphQt.base.port import Port
from NodeGraphQt.widgets.node_backdrop import BackdropNodeItem
from NodeGraphQt.widgets.node_base import NodeItem


class classproperty(object):

    def __init__(self, f):
        self.f = f

    def __get__(self, instance, owner):
        return self.f(owner)


class NodeObject(object):
    """
    The base object of a node.
    """

    __identifier__ = 'nodeGraphQt.nodes'

    NODE_NAME = None

    def __init__(self, node=None):
        assert node, 'node cannot be None.'
        self._graph = None
        self._model = NodeModel()
        self._model.type = self.type
        self._model.name = self.NODE_NAME
        self._view = node
        self._view.type = self.type
        self._view.name = self.model.name
        self._view.id = self._model.id

    def __repr__(self):
        return '{}(\'{}\')'.format(self.type, self.NODE_NAME)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.id == other.id
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    @classproperty
    def type(cls):
        """
        node type identifier followed by the class name.
        eg. com.chantasticvfx.FooNode

        Returns:
            str: node type.
        """
        return cls.__identifier__ + '.' + cls.__name__

    @property
    def graph(self):
        """
        The parent node graph.

        Returns:
            NodeGraphQt.NodeGraph: node graph.
        """
        return self._graph

    @property
    def view(self):
        """
        View item used in the scene.

        Returns:
            QtWidgets.QGraphicsItem: node item.
        """
        return self._view

    def set_view(self, item):
        """
        set the view item for the scene.

        Args:
            item (AbstractNodeItem): node view item.
        """
        self._view = item
        self._view.id = self.model.id
        self.NODE_NAME = self._view.name

    @property
    def model(self):
        """
        returns the node model.

        Returns:
            NodeModel: node model object.
        """
        return self._model

    def set_model(self, model):
        self._model = model
        self._model.type = self.type
        self._model.id = self.view.id

    @property
    def id(self):
        """
        The node unique id.

        Returns:
            str: unique id string.
        """
        return self.model.id

    def update_model(self):
        """
        update the node model from view.
        """
        for name, val in self.view.properties.items():
            if name in self.model.properties.keys():
                setattr(self.model, name, val)
            if name in self.model.custom_properties.keys():
                self.model.custom_properties[name] = val

    def update(self):
        """
        Update the node view from model.
        """
        settings = self.model.to_dict[self.model.id]
        settings['id'] = self.model.id
        if settings.get('custom'):
            settings['widgets'] = settings.pop('custom')

        self.view.from_dict(settings)

    def name(self):
        """
        Name of the node.

        Returns:
            str: name of the node.
        """
        return self.model.name

    def set_name(self, name=''):
        """
        Set the name of the node.

        Args:
            name (str): name for the node.
        """
        self.set_property('name', name)

    def color(self):
        """
        Returns the node color in (red, green, blue) value.

        Returns:
            tuple: (r, g, b) from 0-255 range.
        """
        r, g, b, a = self.model.color
        return r, g, b

    def set_color(self, r=0, g=0, b=0):
        """
        Sets the color of the node in (red, green, blue) value.

        Args:
            r (int): red value 0-255 range.
            g (int): green value 0-255 range.
            b (int): blue value 0-255 range.
        """
        self.set_property('color', (r, g, b, 255))

    def disabled(self):
        """
        returns weather the node is enabled or disabled.

        Returns:
            bool: true if the node is disabled.
        """
        return self.model.disabled

    def set_disabled(self, mode=False):
        """
        disables the node.

        Args (bool): true to disable node.
        """
        self.set_property('disabled', mode)

    def selected(self):
        """
        Returns the selected state of the node.

        Returns:
            bool: True if the node is selected.
        """
        self.model.selected = self.view.isSelected()
        return self.model.selected

    def set_selected(self, selected=True):
        """
        Set the node to be selected or not selected.

        Args:
            selected (bool): True to select the node.
        """
        self.set_property('selected', selected)

    def create_property(self, name, value):
        """
        adds new property to the node.

        Args:
            name (str): name of the attribute.
            value (str, int, float): data
        """
        if not isinstance(name, str):
            raise TypeError('name must of str type.')
        if not isinstance(value, (str, int, float, bool)):
            err = 'value must be of type (String, Integer, Float, Bool)'
            raise TypeError(err)
        elif name in self.view.properties.keys():
            raise KeyError('"{}" property already exists.'.format(name))
        elif name in self.model.properties.keys():
            raise KeyError('"{}" property already exists.'.format(name))
        self.model.custom_properties[name] = value

    def properties(self):
        """
        Returns all the node properties.

        Returns:
            dict: a dictionary of node properties.
        """
        return self.model.to_dict

    def get_property(self, name):
        """
        Return the node custom property.

        Args:
            name (str): name of the property.

        Returns:
            str, int or float: value of the node property.
        """
        if name in self.model.custom_properties.keys():
            if name == 'selected':
                self.model.custom_properties[name] = self.view.selected
            return self.model.custom_properties[name]
        return self.model.properties.get(name)

    def set_property(self, name, value):
        """
        Set the value on the node custom property.

        Args:
            name (str): name of the property.
            value: the new property value.
        """
        if self.graph and name == 'name':
            value = self.graph.get_unique_name(value)
            self.NODE_NAME = value

        exists = any([name in self.model.properties.keys(),
                      name in self.model.custom_properties.keys()])
        if not exists:
            raise KeyError('No property "{}"'.format(name))

        if self.graph:
            undo_stack = self.graph.undo_stack()
            undo_stack.push(PropertyChangedCmd(self, name, value))
        else:
            setattr(self.view, name, value)
            if name in self.model.properties.keys():
                setattr(self.model, name, value)
            elif name in self.model.custom_properties.keys():
                self.model.custom_properties[name] = value

    def has_property(self, name):
        """
        Check if node custom property exists.

        Args:
            name (str): name of the node.

        Returns:
            bool: true if property name exists in the Node.
        """
        return name in self.model.properties.keys()

    def set_x_pos(self, x=0.0):
        """
        Set the node horizontal X position in the node graph.

        Args:
            x (float): node x position:
        """
        y = self.pos()[1]
        self.set_pos(x, y)

    def set_y_pos(self, y=0.0):
        """
        Set the node horizontal Y position in the node graph.

        Args:
            y (float): node x position:
        """

        x = self.pos()[0]
        self.set_pos(x, y)

    def set_pos(self, x=0.0, y=0.0):
        """
        Set the node X and Y position in the node graph.

        Args:
            x (float): node X position.
            y (float): node Y position.
        """
        self.set_property('pos', (x, y))
        # self.view.pos = [x, y]
        # self.model.pos = (x, y)

    def x_pos(self):
        """
        Get the node X position in the node graph.

        Returns:
            float: x position.
        """
        return self.model.pos[0]

    def y_pos(self):
        """
        Get the node Y position in the node graph.

        Returns:
            float: y position.
        """
        return self.model.pos[1]

    def pos(self):
        """
        Get the node XY position in the node graph.

        Returns:
            tuple(float, float): x, y position.
        """
        if self.view.pos and self.view.pos != self.model.pos:
            self.model.pos = self.view.pos

        return self.model.pos


class Node(NodeObject):
    """
    Base class of a typical Node
    """

    NODE_NAME = 'Base Node'

    def __init__(self):
        super(Node, self).__init__(NodeItem())
        self._inputs = []
        self._outputs = []

    def _on_widget_changed(self, name, value):
        self.model.custom_properties[name] = value

    def update_model(self):
        """
        update the node model from view.
        """
        for name, val in self.view.properties.items():
            if name in ['inputs', 'outputs']:
                continue
            if name in self.model.properties.keys():
                setattr(self.model, name, val)
            if name in self.model.custom_properties.keys():
                self.model.custom_properties[name] = val
        for name, widget in self.view.widgets.items():
            if name in self.model.custom_properties.keys():
                self.model.custom_properties[name] = widget.value

    def set_property(self, name, value, update_widget=True):
        """
        Set the value on the node custom property and updates the node widget.

        Args:
            name (str): name of the property.
            value: the new property value.
            update_widget (bool): update the node widget (default=True).
        """
        node_widget = self.view.widgets.get(name)
        if node_widget and update_widget:
            node_widget.value = value
        super(Node, self).set_property(name, value)

    def set_icon(self, icon=None):
        """
        Set the node icon.

        Args:
            icon (str): path to the icon image. 
        """
        self.set_property('icon', icon)

    def icon(self):
        """
        Node icon path.

        Returns:
            str: icon image file path.
        """
        return self.model.icon

    def add_input(self, name='input', multi_input=False, display_name=True):
        """
        Add input port to node.

        Args:
            name (str): name for the input port. 
            multi_input (bool): allow port to have more than one connection.
            display_name (bool): display the port name on the node.
            
        Returns:
            NodeGraphQt.Port: the created port object.
        """
        view = self.view.add_input(name, multi_input, display_name)
        port = Port(self, view)
        port.model.type = 'in'
        port.model.name = name
        port.model.display_name = display_name
        port.model.multi_connection = multi_input
        self._inputs.append(port)
        self.model.inputs[port.name()] = port.model
        return port

    def add_output(self, name='output', multi_output=True, display_name=True):
        """
        Add output port to node.

        Args:
            name (str): name for the output port. 
            multi_output (bool): allow port to have more than one connection.
            display_name (bool): display the port name on the node.
             
        Returns:
            NodeGraphQt.Port: the created port object.
        """
        view = self.view.add_output(name, multi_output, display_name)
        port = Port(self, view)
        port.model.type = 'out'
        port.model.name = name
        port.model.display_name = display_name
        port.model.multi_connection = multi_output
        self._outputs.append(port)
        self.model.outputs[port.name()] = port.model
        return port

    def add_combo_menu(self, name='', label='', items=None):
        """
        Embed a NodeComboBox widget into the node.

        Args:
            name (str): name for the custom property.
            label (str): label to be displayed.
            items (list[str]): items to be added into the menu.
        """
        items = items or []
        self.create_property(name, items[0] if items else '')
        widget = self.view.add_combo_menu(name, label, items)
        widget.value_changed.connect(lambda k, v: self._on_widget_changed(k, v))

    def add_text_input(self, name='', label='', text=''):
        """
        Embed a NodeLineEdit widget into the node.

        Args:
            name (str): name for the custom property.
            label (str): label to be displayed.
            text (str): pre filled text.
        """
        self.create_property(name, text)
        widget = self.view.add_text_input(name, label, text)
        widget.value_changed.connect(lambda k, v: self._on_widget_changed(k, v))

    def add_checkbox(self, name='', label='', text='', state=False):
        """
        Embed a NodeCheckBox widget into the node.

        Args:
            name (str): name for the custom property.
            label (str): label to be displayed.
            text (str): checkbox text.
            state (bool): pre-check.
        """
        self.create_property(name, state)
        widget = self.view.add_checkbox(name, label, text, state)
        widget.value_changed.connect(lambda k, v: self._on_widget_changed(k, v))

    def inputs(self):
        """
        Returns all the input port for the node.
        
        Returns:
            dict: {<port_name>: <port_object>}
        """
        return {p.name(): p for p in self._inputs}

    def outputs(self):
        """
        Returns all the output port for the node.

        Returns:
            dict: {<port_name>: <port_object>}
        """
        return {p.name(): p for p in self._outputs}

    def input(self, index):
        """
        Return the input port with the matching index.

        Args:
            index (int): index of the input port.

        Returns:
            NodeGraphQt.Port: port object.
        """
        return self._inputs[index]

    def set_input(self, index, port):
        """
        Creates a connection pipe to the targeted output port.

        Args:
            index (int): index of the port.
            port (NodeGraphQt.Port): port object.
        """
        src_port = self.input(index)
        src_port.connect_to(port)

    def output(self, index):
        """
        Return the output port with the matching index.

        Args:
            index (int): index of the output port.

        Returns:
            NodeGraphQt.Port: port object.
        """
        return self._outputs[index]

    def set_output(self, index, port):
        """
        Creates a connection pipe to the targeted input port.

        Args:
            index (int): index of the port.
            port (NodeGraphQt.Port): port object.
        """
        src_port = self.output(index)
        src_port.connect_to(port)


class Backdrop(NodeObject):
    """
    Base class of a Backdrop.
    """

    NODE_NAME = 'Backdrop'

    def __init__(self):
        super(Backdrop, self).__init__(BackdropNodeItem())
        # override base default color.
        self.model.color = (5, 129, 138, 255)
        self.create_property('bg_text', '')

    def auto_size(self):
        """
        Auto resize the backdrop node to fit around the intersecting nodes.
        """
        self.view.auto_resize()

    def nodes(self):
        """
        Returns nodes wrapped within the backdrop node.

        Returns:
            list[NodeGraphQt.Node]: list of node under the backdrop.
        """
        node_ids = [n.id for n in self.view.get_nodes()]
        return [self.graph.get_node_by_id(nid) for nid in node_ids]

    def set_text(self, text=''):
        """
        Sets the text to be displayed in the backdrop node.

        Args:
            text (str): text string.
        """
        self.set_property('backdrop_text', text)

    def text(self):
        """
        Returns the text on the backdrop node.

        Returns:
            str: text string.
        """
        return self.get_property('backdrop_text')

    def set_size(self, size=None):
        """
        Sets the backdrop size.

        Args:
            size (tuple): width, height size.
        """
        if size:
            if self.graph:
                self.graph.begin_undo('backdrop size')
                self.set_property('width', size[0])
                self.set_property('height', size[1])
                self.graph.end_undo()
                return
            self.view.width, self.view.height = size
            self.model.width, self.model.height = size

    def size(self):
        """
        Returns the current size of the node.

        Returns:
            tuple: node width, height
        """
        self.model.width = self.view.width
        self.model.height = self.view.height
        return self.model.width, self.model.height

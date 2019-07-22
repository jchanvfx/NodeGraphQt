#!/usr/bin/python
from NodeGraphQt.base.commands import PropertyChangedCmd
from NodeGraphQt.base.model import NodeModel
from NodeGraphQt.base.port import Port
from NodeGraphQt.constants import (NODE_PROP,
                                   NODE_PROP_QLINEEDIT,
                                   NODE_PROP_QTEXTEDIT,
                                   NODE_PROP_QCOMBO,
                                   NODE_PROP_QCHECKBOX,
                                   IN_PORT, OUT_PORT)
from NodeGraphQt.errors import PortRegistrationError
from NodeGraphQt.qgraphics.node_backdrop import BackdropNodeItem
from NodeGraphQt.qgraphics.node_base import NodeItem
from NodeGraphQt.widgets.node_property import (NodeComboBox,
                                               NodeLineEdit,
                                               NodeCheckBox)


class classproperty(object):

    def __init__(self, f):
        self.f = f

    def __get__(self, instance, owner):
        return self.f(owner)


class NodeObject(object):
    """
    base class for all node objects.

    Args:
        qgraphics_item (AbstractNodeItem): graphic item used for drawing.
    """

    #: (str) unique node identifier domain.
    __identifier__ = 'nodeGraphQt.nodes'

    #: (str) base node name.
    NODE_NAME = None

    def __init__(self, qgraphics_item=None):
        assert qgraphics_item, 'qgraphics item cannot be None.'
        self._graph = None
        self._model = NodeModel()
        self._model.type_ = self.type_
        self._model.name = self.NODE_NAME
        self._view = qgraphics_item
        self._view.type_ = self.type_
        self._view.name = self.model.name
        self._view.id = self._model.id

    def __repr__(self):
        return '<{}("{}") object at {}>'.format(
            self.__class__.__name__, self.NODE_NAME, hex(id(self)))

    @classproperty
    def type_(cls):
        """
        Node type identifier followed by the class name.
        eg. nodeGraphQt.nodes.MyNode

        Returns:
            str: node type.
        """
        return cls.__identifier__ + '.' + cls.__name__

    @property
    def id(self):
        """
        The node unique id.

        Returns:
            str: unique id string.
        """
        return self.model.id

    @property
    def graph(self):
        """
        The parent node graph controller.

        Returns:
            NodeGraphQt.NodeGraph: node graph.
        """
        return self._graph

    @property
    def view(self):
        """
        Returns the :class:`QtWidgets.QGraphicsItem` used in the scene.

        Returns:
            NodeGraphQt.qgraphics.node_abstract.AbstractNodeItem: node item.
        """
        return self._view

    def set_view(self, item):
        """
        Sets the qgraphics item to use for the scene.

        Args:
            item (NodeGraphQt.qgraphics.node_abstract.AbstractNodeItem): node item.
        """
        self._view = item
        self._view.id = self.model.id
        self.NODE_NAME = self._view.name

    @property
    def model(self):
        """
        Return the node model.

        Returns:
            NodeGraphQt.base.model.NodeModel: node model object.
        """
        return self._model

    def set_model(self, model):
        """
        Set the node model.

        Args:
            model (NodeGraphQt.base.model.NodeModel): node model object.
        """
        self._model = model
        self._model.type_ = self.type_
        self._model.id = self.view.id

    def update_model(self):
        """
        Update the node model from view.
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
        Returns weather the node is enabled or disabled.

        Returns:
            bool: true if the node is disabled.
        """
        return self.model.disabled

    def set_disabled(self, mode=False):
        """
        Set the node state to either disabled or enabled.

        Args:
            mode(bool): true to disable node.
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

    def create_property(self, name, value, items=None, range=None,
                        widget_type=NODE_PROP, tab=None):
        """
        Creates a custom property to the node.

        Args:
            name (str): name of the property.
            value (object): data.
            items (list[str]): items used by widget type NODE_PROP_QCOMBO
            range (tuple)): min, max values used by NODE_PROP_SLIDER
            widget_type (int): widget flag to display in the properties bin.
            tab (str): name of the widget tab to display in the properties bin.
        """
        self.model.add_property(name, value, items, range, widget_type, tab)

    def properties(self):
        """
        Returns all the node properties.

        Returns:
            dict: a dictionary of node properties.
        """
        props = self.model.to_dict[self.id].copy()
        props['id'] = self.id
        return props

    def get_property(self, name):
        """
        Return the node custom property.

        Args:
            name (str): name of the property.

        Returns:
            object: property data.
        """
        if self.graph and name == 'selected':
            self.model.set_property(self.view.selected)

        return self.model.get_property(name)

    def set_property(self, name, value):
        """
        Set the value on the node custom property.

        Args:
            name (str): name of the property.
            value (object): property data.
        """

        # prevent signals from causing a infinite loop.
        if self.get_property(name) == value:
            return

        if self.graph and name == 'name':
            value = self.graph.get_unique_name(value)
            self.NODE_NAME = value

        if self.graph:
            undo_stack = self.graph.undo_stack()
            undo_stack.push(PropertyChangedCmd(self, name, value))
        else:
            if hasattr(self.view, name):
                setattr(self.view, name, value)
            self.model.set_property(name, value)

    def has_property(self, name):
        """
        Check if node custom property exists.

        Args:
            name (str): name of the node.

        Returns:
            bool: true if property name exists in the Node.
        """
        return name in self.model.properties.keys()

    def set_x_pos(self, x):
        """
        Set the node horizontal X position in the node graph.

        Args:
            x (float or int): node X position:
        """
        y = self.pos()[1]
        self.set_pos(float(x), y)

    def set_y_pos(self, y):
        """
        Set the node horizontal Y position in the node graph.

        Args:
            y (float or int): node Y position:
        """

        x = self.pos()[0]
        self.set_pos(x, float(y))

    def set_pos(self, x, y):
        """
        Set the node X and Y position in the node graph.

        Args:
            x (float or int): node X position.
            y (float or int): node Y position.
        """
        self.set_property('pos', [float(x), float(y)])

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
            list[float, float]: x, y position.
        """
        if self.view.xy_pos and self.view.xy_pos != self.model.pos:
            self.model.pos = self.view.xy_pos

        return self.model.pos


class BaseNode(NodeObject):
    """
    base class of a typical Node with input and output ports.
    """

    NODE_NAME = 'Base Node'

    def __init__(self):
        super(BaseNode, self).__init__(NodeItem())
        self._inputs = []
        self._outputs = []

    def update_model(self):
        """
        update the node model from view.
        """
        for name, val in self.view.properties.items():
            if name in ['inputs', 'outputs']:
                continue
            self.model.set_property(name, val)

        for name, widget in self.view.widgets.items():
            self.model.set_property(name, widget.value)

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

    def add_combo_menu(self, name='', label='', items=None, tab=None):
        """
        Create a custom property and embed a
        :class:`PySide2.QtWidgets.QComboBox` widget into the node.

        Args:
            name (str): name for the custom property.
            label (str): label to be displayed.
            items (list[str]): items to be added into the menu.
            tab (str): name of the widget tab to display in.
        """
        items = items or []
        self.create_property(
            name, items[0], items=items, widget_type=NODE_PROP_QCOMBO, tab=tab)

        widget = NodeComboBox(self.view, name, label, items)
        widget.value_changed.connect(lambda k, v: self.set_property(k, v))
        self.view.add_widget(widget)

    def add_text_input(self, name='', label='', text='', tab=None):
        """
        Create a custom property and embed a
        :class:`PySide2.QtWidgets.QLineEdit` widget into the node.

        Args:
            name (str): name for the custom property.
            label (str): label to be displayed.
            text (str): pre filled text.
            tab (str): name of the widget tab to display in.
        """
        self.create_property(
            name, text, widget_type=NODE_PROP_QLINEEDIT, tab=tab)
        widget = NodeLineEdit(self.view, name, label, text)
        widget.value_changed.connect(lambda k, v: self.set_property(k, v))
        self.view.add_widget(widget)

    def add_checkbox(self, name='', label='', text='', state=False, tab=None):
        """
        Create a custom property and embed a
        :class:`PySide2.QtWidgets.QCheckBox` widget into the node.

        Args:
            name (str): name for the custom property.
            label (str): label to be displayed.
            text (str): checkbox text.
            state (bool): pre-check.
            tab (str): name of the widget tab to display in.
        """
        self.create_property(
            name, state, widget_type=NODE_PROP_QCHECKBOX, tab=tab)
        widget = NodeCheckBox(self.view, name, label, text, state)
        widget.value_changed.connect(lambda k, v: self.set_property(k, v))
        self.view.add_widget(widget)

    def add_input(self, name='input', multi_input=False, display_name=True,
                  color=None):
        """
        Add input :class:`Port` to node.

        Args:
            name (str): name for the input port.
            multi_input (bool): allow port to have more than one connection.
            display_name (bool): display the port name on the node.
            color (tuple): initial port color (r, g, b) 0-255.

        Returns:
            NodeGraphQt.Port: the created port object.
        """
        if name in self.inputs().keys():
            raise PortRegistrationError(
                'port name "{}" already registered.'.format(name))
        view = self.view.add_input(name, multi_input, display_name)
        if color:
            view.color = color
            view.border_color = [min([255, max([0, i + 80])]) for i in color]
        port = Port(self, view)
        port.model.type_ = IN_PORT
        port.model.name = name
        port.model.display_name = display_name
        port.model.multi_connection = multi_input
        self._inputs.append(port)
        self.model.inputs[port.name()] = port.model
        return port

    def add_output(self, name='output', multi_output=True, display_name=True,
                   color=None):
        """
        Add output :class:`Port` to node.

        Args:
            name (str): name for the output port.
            multi_output (bool): allow port to have more than one connection.
            display_name (bool): display the port name on the node.
            color (tuple): initial port color (r, g, b) 0-255.

        Returns:
            NodeGraphQt.Port: the created port object.
        """
        if name in self.outputs().keys():
            raise PortRegistrationError(
                'port name "{}" already registered.'.format(name))
        view = self.view.add_output(name, multi_output, display_name)
        if color:
            view.color = color
            view.border_color = [min([255, max([0, i + 80])]) for i in color]
        port = Port(self, view)
        port.model.type_ = OUT_PORT
        port.model.name = name
        port.model.display_name = display_name
        port.model.multi_connection = multi_output
        self._outputs.append(port)
        self.model.outputs[port.name()] = port.model
        return port

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
        Creates a connection pipe to the targeted output :class:`Port`.

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
        Creates a connection pipe to the targeted input :class:`Port`.

        Args:
            index (int): index of the port.
            port (NodeGraphQt.Port): port object.
        """
        src_port = self.output(index)
        src_port.connect_to(port)


class BackdropNode(NodeObject):
    """
    base class of a Backdrop node.
    """

    NODE_NAME = 'Backdrop'

    def __init__(self):
        super(BackdropNode, self).__init__(BackdropNodeItem())
        # override base default color.
        self.model.color = (5, 129, 138, 255)
        self.create_property('backdrop_text', '',
                             widget_type=NODE_PROP_QTEXTEDIT, tab='Backdrop')

    def auto_size(self):
        """
        Auto resize the backdrop node to fit around the intersecting nodes.
        """
        self.view.auto_resize()

    def nodes(self):
        """
        Returns nodes wrapped within the backdrop node.

        Returns:
            list[NodeGraphQt.BaseNode]: list of node under the backdrop.
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

    def set_size(self, width, height):
        """
        Sets the backdrop size.

        Args:
            width (float): backdrop width size.
            height (float): backdrop height size.
        """
        if self.graph:
            self.graph.begin_undo('backdrop size')
            self.set_property('width', width)
            self.set_property('height', height)
            self.graph.end_undo()
            return
        self.view.width, self.view.height = width, height
        self.model.width, self.model.height = width, height

    def size(self):
        """
        Returns the current size of the node.

        Returns:
            tuple: node width, height
        """
        self.model.width = self.view.width
        self.model.height = self.view.height
        return self.model.width, self.model.height

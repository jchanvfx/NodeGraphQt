#!/usr/bin/python
from .commands import PropertyChangedCmd
from .model import NodeModel
from .port import Port
from ..constants import (NODE_PROP,
                         NODE_PROP_QLINEEDIT,
                         NODE_PROP_QTEXTEDIT,
                         NODE_PROP_QCOMBO,
                         NODE_PROP_QCHECKBOX,
                         NODE_PROP_FILE,
                         NODE_PROP_FLOAT,
                         NODE_PROP_INT,
                         IN_PORT, OUT_PORT)
from ..errors import PortRegistrationError
from ..qgraphics.node_backdrop import BackdropNodeItem
from ..qgraphics.node_base import NodeItem
from ..widgets.node_widgets import (NodeComboBox,
                                    NodeLineEdit,
                                    NodeFloatEdit,
                                    NodeIntEdit,
                                    NodeCheckBox,
                                    NodeFilePath)


class classproperty(object):

    def __init__(self, f):
        self.f = f

    def __get__(self, instance, owner):
        return self.f(owner)


class NodeObject(object):
    """
    The ``NodeGraphQt.NodeObject`` class is the main base class that all
    nodes inherit from.

    **Inherited by:** :class:`NodeGraphQt.BaseNode`, :class:`NodeGraphQt.BackdropNode`

    Args:
        qgraphics_item (AbstractNodeItem): graphic item used for drawing.
    """

    # Unique node identifier domain. `eg.` ``"com.chantacticvfx"``
    __identifier__ = 'nodeGraphQt.nodes'

    # Base node name.
    NODE_NAME = None

    def __init__(self, qgraphics_item=None):
        assert qgraphics_item, 'qgraphics_item item cannot be None.'
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
        `eg.` ``"com.chantacticvfx.NodeObject"``

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
        The parent node graph.

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

    def set_graph(self, graph):
        self._graph = graph

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
            tuple: ``(r, g, b)`` from ``0-255`` range.
        """
        r, g, b, a = self.model.color
        return r, g, b

    def set_color(self, r=0, g=0, b=0):
        """
        Sets the color of the node in (red, green, blue) value.

        Args:
            r (int): red value ``0-255`` range.
            g (int): green value ``0-255`` range.
            b (int): blue value ``0-255`` range.
        """
        self.set_property('color', (r, g, b, 255))

    def disabled(self):
        """
        Returns weather the node is enabled or disabled.

        Returns:
            bool: True if the node is disabled.
        """
        return self.model.disabled

    def set_disabled(self, mode=False):
        """
        Set the node state to either disabled or enabled.

        Args:
            mode(bool): True to disable node.
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
                        widget_type=NODE_PROP, tab=None, ext=None,
                        funcs=None):
        """
        Creates a custom property to the node.

        Widget Types:
            - :attr:`NodeGraphQt.constants.NODE_PROP`
            - :attr:`NodeGraphQt.constants.NODE_PROP_QLABEL`
            - :attr:`NodeGraphQt.constants.NODE_PROP_QLINEEDIT`
            - :attr:`NodeGraphQt.constants.NODE_PROP_QTEXTEDIT`
            - :attr:`NodeGraphQt.constants.NODE_PROP_QCOMBO`
            - :attr:`NodeGraphQt.constants.NODE_PROP_QCHECKBOX`
            - :attr:`NodeGraphQt.constants.NODE_PROP_QSPINBOX`
            - :attr:`NodeGraphQt.constants.NODE_PROP_COLORPICKER`
            - :attr:`NodeGraphQt.constants.NODE_PROP_FILE`
            - :attr:`NodeGraphQt.constants.NODE_PROP_VECTOR2`
            - :attr:`NodeGraphQt.constants.NODE_PROP_VECTOR3`
            - :attr:`NodeGraphQt.constants.NODE_PROP_VECTOR4`
            - :attr:`NodeGraphQt.constants.NODE_PROP_FLOAT`
            - :attr:`NodeGraphQt.constants.NODE_PROP_INT`
            - :attr:`NodeGraphQt.constants.NODE_PROP_BUTTON`

        See Also:
            :class:`NodeGraphQt.PropertiesBinWidget`

        Args:
            name (str): name of the property.
            value (object): data.
            items (list[str]): items used by widget type ``NODE_PROP_QCOMBO``
            range (tuple)): ``(min, max)`` values used by ``NODE_PROP_SLIDER``
            widget_type (int): widget flag to display in the ``PropertiesBinWidget``
            tab (str): name of the widget tab to display in the properties bin.
            ext (str): file ext of ``NODE_PROP_FILE``
            funcs (list) list of functions for NODE_PROP_BUTTON
        """
        self.model.add_property(name, value, items, range, widget_type, tab, ext, funcs)

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
            self.model.set_property(name, self.view.selected)

        return self.model.get_property(name)

    def set_property(self, name, value):
        """
        Set the value on the node custom property.

        Args:
            name (str): name of the property.
            value (object): property data.
        """

        # prevent signals from causing a infinite loop.
        try:
            if self.get_property(name) == value:
                return
        except:
            pass

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
        return name in self.model.custom_properties.keys()

    def set_x_pos(self, x):
        """
        Set the node horizontal X position in the node graph.

        Args:
            x (float or int): node X position.
        """
        y = self.pos()[1]
        self.set_pos(float(x), y)

    def set_y_pos(self, y):
        """
        Set the node horizontal Y position in the node graph.

        Args:
            y (float or int): node Y position.
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
    The ``NodeGraphQt.BaseNode`` class is the base class for nodes that allows
    port connections from one node to another.

    **Inherited from:** :class:`NodeGraphQt.NodeObject`

    .. image:: ../_images/node.png
        :width: 250px

    example snippet:

    .. code-block:: python
        :linenos:

        from NodeGraphQt import BaseNode

        class FooNode(BaseNode):

            # unique node identifier domain.
            __identifier__ = 'com.chantasticvfx'

            # initial default node name.
            NODE_NAME = 'Foo Node'

            def __init__(self):
                super(FooNode, self).__init__()

                # create an input port.
                self.add_input('in')

                # create an output port.
                self.add_output('out')
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

    def widgets(self):
        """
        Returns all embedded widgets from this node.

        See Also:
            :meth:`BaseNode.get_widget`

        Returns:
            dict: embedded node widgets. {``property_name``: ``node_widget``}
        """
        return self.view.widgets

    def get_widget(self, name):
        """
        Returns the embedded widget associated with the property name.

        See Also:
            :meth:`BaseNode.add_combo_menu`,
            :meth:`BaseNode.add_text_input`,
            :meth:`BaseNode.add_checkbox`,

        Args:
            name (str): node property name.

        Returns:
            NodeBaseWidget: embedded node widget.
        """
        return self.view.widgets.get(name)

    def add_combo_menu(self, name, label='', items=None, tab=None):
        """
        Creates a custom property with the :meth:`NodeObject.create_property`
        function and embeds a :class:`PySide2.QtWidgets.QComboBox` widget
        into the node.

        Note:
            The embedded widget is wired up to the :meth:`NodeObject.set_property`
            function use this function to to update the widget.

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

    def add_text_input(self, name, label='', text='', tab=None, multi_line=False):
        """
        Creates a custom property with the :meth:`NodeObject.create_property`
        function and embeds a :class:`PySide2.QtWidgets.QLineEdit` widget
        into the node.

        Note:
            The embedded widget is wired up to the :meth:`NodeObject.set_property`
            function use this function to to update the widget.

        Args:
            name (str): name for the custom property.
            label (str): label to be displayed.
            text (str): pre filled text.
            tab (str): name of the widget tab to display in.
            multi_line (bool): if create multi line property.
        """
        wid_type = NODE_PROP_QTEXTEDIT if multi_line else NODE_PROP_QLINEEDIT

        self.create_property(
            name, text, widget_type=wid_type, tab=tab)
        widget = NodeLineEdit(self.view, name, label, text)
        widget.value_changed.connect(lambda k, v: self.set_property(k, v))
        self.view.add_widget(widget)

    def add_file_input(self, name, label='', text='', tab=None, ext="*"):
        """
        Creates a custom property with the :meth:`NodeObject.create_property`
        function and embeds a :class:`PySide2.QtWidgets.QLineEdit` widget
        into the node.

        Note:
            The embedded widget is wired up to the :meth:`NodeObject.set_property`
            function use this function to to update the widget.

        Args:
            name (str): name for the custom property.
            label (str): label to be displayed.
            text (str): pre filled text.
            tab (str): name of the widget tab to display in.
            ext (str): file ext
        """
        self.create_property(
            name, text, widget_type=NODE_PROP_FILE, tab=tab, ext=ext)
        widget = NodeFilePath(self.view, name, label, text, ext)
        widget.value_changed.connect(lambda k, v: self.set_property(k, v))
        self.view.add_widget(widget)

    def add_float_input(self, name, label='', value=0.0, range=None, tab=None):
        """
        Creates a custom property with the :meth:`NodeObject.create_property`
        function and embeds a :class:`PySide2.QtWidgets.QLineEdit` widget
        into the node.

        Note:
            The embedded widget is wired up to the :meth:`NodeObject.set_property`
            function use this function to to update the widget.

        Args:
            name (str): name for the custom property.
            label (str): label to be displayed.
            value (float): pre filled value.
            range (tuple): slider range
            tab (str): name of the widget tab to display in.
        """
        self.create_property(
            name, value, widget_type=NODE_PROP_FLOAT, range=range, tab=tab)
        widget = NodeFloatEdit(self.view, name, label, value)
        widget.value_changed.connect(lambda k, v: self.set_property(k, v))
        self.view.add_widget(widget)

    def add_int_input(self, name, label='', value=0, range=None, tab=None):
        """
        Creates a custom property with the :meth:`NodeObject.create_property`
        function and embeds a :class:`PySide2.QtWidgets.QLineEdit` widget
        into the node.

        Note:
            The embedded widget is wired up to the :meth:`NodeObject.set_property`
            function use this function to to update the widget.

        Args:
            name (str): name for the custom property.
            label (str): label to be displayed.
            value (int): pre filled value.
            range (tuple): slider range
            tab (str): name of the widget tab to display in.
        """
        self.create_property(
            name, value, widget_type=NODE_PROP_INT, range=range, tab=tab)
        widget = NodeIntEdit(self.view, name, label, value)
        widget.value_changed.connect(lambda k, v: self.set_property(k, v))
        self.view.add_widget(widget)

    def add_checkbox(self, name, label='', text='', state=False, tab=None):
        """
        Creates a custom property with the :meth:`NodeObject.create_property`
        function and embeds a :class:`PySide2.QtWidgets.QCheckBox` widget
        into the node.

        Note:
            The embedded widget is wired up to the :meth:`NodeObject.set_property`
            function use this function to to update the widget.

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
            color (tuple): initial port color (r, g, b) ``0-255``.

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
            color (tuple): initial port color (r, g, b) ``0-255``.

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

    def update_combo_menu(self, name, items):
        if not self.has_property(name):
            return
        old_value = self.get_property(name)
        self.set_property(name, items)
        _name = '_' + name + "_"
        if not self.has_property(_name):
            self.create_property(_name, items)
        else:
            self.set_property(_name, items)
        if old_value in items:
            self.set_property(name, old_value)
        else:
            self.set_property(name, items[0])

    def inputs(self):
        """
        Returns all the input ports from the node.
        
        Returns:
            dict: {<port_name>: <port_object>}
        """
        return {p.name(): p for p in self._inputs}

    def input_ports(self):
        """
        Return all input ports.

        Returns:
            list[NodeGraphQt.Port]: node input ports.
        """
        return self._inputs

    def outputs(self):
        """
        Returns all the output ports from the node.

        Returns:
            dict: {<port_name>: <port_object>}
        """
        return {p.name(): p for p in self._outputs}

    def output_ports(self):
        """
        Return all output ports.

        Returns:
            list[NodeGraphQt.Port]: node output ports.
        """
        return self._outputs

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

    def connected_input_nodes(self):
        """
        Returns all nodes connected from the input ports.

        Returns:
            dict: {<input_port>: <node_list>}
        """
        nodes = {}
        for p in self.input_ports():
            nodes[p] = [cp.node() for cp in p.connected_ports()]
        return nodes

    def connected_output_nodes(self):
        """
        Returns all nodes connected from the output ports.

        Returns:
            dict: {<output_port>: <node_list>}
        """
        nodes = {}
        for p in self.output_ports():
            nodes[p] = [cp.node() for cp in p.connected_ports()]
        return nodes

    def on_input_connected(self, in_port, out_port):
        """
        Callback triggered when a new pipe connection is made.

        *The default of this function does nothing re-implement if you require
        logic to run for this event.*

        Note:
            to work with undo & redo for this method re-implement
            :meth:`BaseNode.on_input_disconnected` with the reverse logic.

        Args:
            in_port (NodeGraphQt.Port): source input port from this node.
            out_port (NodeGraphQt.Port): output port that connected to this node.
        """
        return

    def on_input_disconnected(self, in_port, out_port):
        """
        Callback triggered when a pipe connection has been disconnected
        from a INPUT port.

        *The default of this function does nothing re-implement if you require
        logic to run for this event.*

        Note:
            to work with undo & redo for this method re-implement
            :meth:`BaseNode.on_input_connected` with the reverse logic.

        Args:
            in_port (NodeGraphQt.Port): source input port from this node.
            out_port (NodeGraphQt.Port): output port that was disconnected.
        """
        return

    def update_streams(self, *args):
        """
        Update all nodes joined by pipes to this.
        """
        nodes = []
        trash = []

        for port, nodeList in self.connected_output_nodes().items():
            nodes.extend(nodeList)

        while nodes:
            node = nodes.pop()
            if node.disabled():
                continue
            if node not in trash:
                trash.append(node)

            for port, nodeList in node.connected_output_nodes().items():
                nodes.extend(nodeList)

            if not node.connected_output_nodes():
                try:
                    node.run()
                except Exception as error:
                    print("Error Update Streams: %s" % str(error))

    def run(self):
        """
        Node evaluation logics.
        """
        return


class BackdropNode(NodeObject):
    """
    The ``NodeGraphQt.BackdropNode`` class allows other node object to be
    nested inside, it's mainly good for grouping nodes together.

    **Inherited from:** :class:`NodeGraphQt.NodeObject`

    .. image:: ../_images/backdrop.png
        :width: 250px
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

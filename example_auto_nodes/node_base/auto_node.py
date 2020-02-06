from NodeGraphQt.base.node import BaseNode
from NodeGraphQt.base.port import Port
from NodeGraphQt.constants import NODE_PROP
from NodeGraphQt import QtCore
import random
import copy
import time

def rand_color(seed_type):
    seed = id(seed_type)
    random.seed(seed + 10)
    r = random.randint(50, 200)
    random.seed(seed + 5)
    g = random.randint(50, 200)
    random.seed(seed + 3421)
    b = random.randint(50, 200)
    return (r, g, b, 255)


class AutoNode(BaseNode,QtCore.QObject):
    cooked = QtCore.Signal()

    def __init__(self, defaultInputType=None, defaultOutputType=None):
        super(AutoNode, self).__init__()
        QtCore.QObject.__init__(self)
        self.needCook = True
        self._autoCook = True
        self._error = False
        self.matchTypes = [[float, int]]
        self.errorColor = (200, 50, 50)
        self.stopCookColor = (200, 200, 200)

        self.defaultColor = self.get_property("color")
        self.defaultValue = None
        self.defaultInputType = defaultInputType
        self.defaultOutputType = defaultOutputType

        self._cookTime = 0.0
        self._toolTip = self._setup_tool_tip()

    @property
    def autoCook(self):
        return self._autoCook

    @autoCook.setter
    def autoCook(self, mode):
        if mode is self._autoCook:
            return

        self._autoCook = mode
        if mode:
            self.set_property('color', self.defaultColor)
        else:
            self.defaultColor = self.get_property("color")
            self.set_property('color', self.stopCookColor)

    @property
    def cookTime(self):
        return self._cookTime

    @autoCook.setter
    def cookTime(self, time):
        self._cookTime = time
        self._update_tool_tip()

    def cookNextNode(self):
        for nodeList in self.connected_output_nodes().values():
            for n in nodeList:
                n.cook()

    def getInputData(self, port):
        # get input data by input Port,the type of "port" can be :
        # int : Port index
        # str : Port name
        # Port : Port object

        if type(port) is int:
            to_port = self.input(port)
        elif type(port) is str:
            to_port = self.inputs()[port]
        elif type(port) is Port:
            to_port = port
        else:
            print(self.inputs().keys())
            return self.defaultValue

        from_ports = to_port.connected_ports()
        if not from_ports:
            return copy.deepcopy(self.defaultValue)

        for from_port in from_ports:
            data = from_port.node().get_property(from_port.name())
            return copy.deepcopy(data)

    def when_disabled(self):
        num = len(self.input_ports())
        for index, out_port in enumerate(self.output_ports()):
            self.set_property(out_port.name(), self.getInputData(index % num))

    def cook(self, forceCook=False):
        if not self._autoCook and forceCook is not True:
            return

        _tmp = self._autoCook
        self._autoCook = False

        if self.disabled():
            self._autoCook = _tmp
            self.when_disabled()
            self.cookNextNode()
            return

        if not self.needCook:
            self._autoCook = _tmp
            return

        if self.error():
            self._close_error()

        _start_time = time.time()

        try:
            self.run()
        except Exception as error:
            self.error(error)
        self._autoCook = _tmp

        if self.error():
            return

        self.cookTime = time.time() - _start_time

        self.cooked.emit()
        self.cookNextNode()

    def run(self):
        pass

    def on_input_connected(self, to_port, from_port):
        if self.checkPortType(to_port, from_port):
            self.cook()
        else:
            self.needCook = False
            to_port.disconnect_from(from_port)

    def on_input_disconnected(self, to_port, from_port):
        if not self.needCook:
            self.needCook = True
            return
        self.cook()

    def set_disabled(self, mode=False):
        super(AutoNode, self).set_disabled(mode)
        if self.input_ports():
            self.cook()

    def checkPortType(self, to_port, from_port):
        # None type port can connect with any other type port
        # types in self.matchTypes can connect with each other

        if hasattr(to_port, "DataType") and hasattr(from_port, "DataType"):
            if to_port.DataType is not from_port.DataType:
                for types in self.matchTypes:
                    if to_port.DataType in types and from_port.DataType in types:
                        return True
                return False

        return True

    def set_property(self, name, value):
        super(AutoNode, self).set_property(name, value)
        self.set_port_type(name, type(value))
        if name in self.model.custom_properties.keys():
            self.cook()

    def set_port_type(self, port, value_type):
        current_port = None

        if type(port) is Port:
            current_port = port
        elif type(port) is str:
            inputs = self.inputs()
            outputs = self.outputs()
            if port in inputs.keys():
                current_port = inputs[port]
            elif port in outputs.keys():
                current_port = outputs[port]

        if current_port:
            if hasattr(current_port, "DataType"):
                if current_port.DataType is value_type:
                    return
            else:
                current_port.DataType = value_type

            current_port.border_color = rand_color(value_type)
            current_port.color = rand_color(value_type)
            conn_type = 'multi' if current_port.multi_connection() else 'single'
            data_type_name = value_type.__name__ if value_type else "all"
            current_port.view.setToolTip('{}: {} ({}) '.format(current_port.name(), data_type_name, conn_type))

    def create_property(self, name, value, items=None, range=None,
                        widget_type=NODE_PROP, tab=None):
        super(AutoNode, self).create_property(name, value, items, range, widget_type, tab)

        if value is not None:
            self.set_port_type(name, type(value))

    def add_input(self, name='input', data_type=None, multi_input=False, display_name=True,
                  color=None):
        new_port = super(AutoNode, self).add_input(name, multi_input, display_name, color)
        if data_type:
            self.set_port_type(new_port, data_type)
        elif self.defaultInputType:
            self.set_port_type(new_port, self.defaultInputType)
        return new_port

    def add_output(self, name='output', data_type=None, multi_output=True, display_name=True,
                   color=None):
        new_port = super(AutoNode, self).add_output(name, multi_output, display_name, color)
        if data_type:
            self.set_port_type(new_port, data_type)
        elif self.defaultOutputType:
            self.set_port_type(new_port, self.defaultOutputType)
        return new_port

    def _close_error(self):
        self._error = False
        self.set_property('color', self.defaultColor)
        self._update_tool_tip()

    def _show_error(self, message):
        if not self._error:
            self.defaultColor = self.get_property("color")

        self._error = True
        self.set_property('color', self.errorColor)
        tooltip = '<font color="red"><br>({})</br></font>'.format(message)
        self._update_tool_tip(tooltip)

    def _update_tool_tip(self, message = None):
        if message is None:
            tooltip = self._toolTip.format(self._cookTime)
        else:
            tooltip = '<b>{}</b>'.format(self.name())
            tooltip += message
            tooltip += '<br/>{}<br/>'.format(self._view.type_)
        self.view.setToolTip(tooltip)
        return tooltip

    def _setup_tool_tip(self):
        tooltip = '<br> last cook used: {}s</br>'
        return self._update_tool_tip(tooltip)

    def error(self, message=None):
        if message is None:
            return self._error

        self._show_error(message)

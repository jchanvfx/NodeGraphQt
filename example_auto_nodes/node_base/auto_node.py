from NodeGraphQt.base.node import BaseNode
from NodeGraphQt.base.port import Port
from NodeGraphQt.constants import NODE_PROP
import random


def rand_color(seed_type):
    seed = id(seed_type)
    random.seed(seed+10)
    r = random.randint(50, 200)
    random.seed(seed + 5)
    g = random.randint(50, 200)
    random.seed(seed + 3421)
    b = random.randint(50, 200)
    return (r, g, b, 255)


class AutoNode(BaseNode):
    def __init__(self,defaultInputType=None,defaultOutputType=None):
        super(AutoNode, self).__init__()
        self.needCook = True
        self._error = False
        self.matchTypes = [[float, int]]
        self.errorColor = (200, 50, 50)

        self.defaultColor = self.get_property("color")
        self.defaultValue = None
        self.defaultInputType = defaultInputType
        self.defaultOutputType = defaultOutputType

    def cookNextNode(self):
        for nodeList in self.connected_output_nodes().values():
            for n in nodeList:
                n.cook()

    def getInputData(self, port):
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
            return self.defaultValue

        for from_port in from_ports:
            data = from_port.node().get_property(from_port.name())
            return data

    def cook(self):
        if self.disabled():
            num = len(self.input_ports())
            for index, out_port in enumerate(self.output_ports()):
                self.set_property(out_port.name(), self.getInputData(index % num))
            self.cookNextNode()
            return

        if not self.needCook:
            return

        if self.error():
            self._close_error()

        self.run()

        if self.error():
            return

        self.cookNextNode()


    def run(self):
        pass
        #print("RUN {} Node".format(self.name()))

    def on_input_connected(self, to_port, from_port):
        if self.checkPortType(to_port, from_port):
            self.cook()
        else:
            self.needCook = False
            self.graph._on_connection_changed([(from_port.view, to_port.view)], [])

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
        if hasattr(to_port,"DataType") and hasattr(from_port,"DataType"):
            if to_port.DataType is not from_port.DataType:
                for types in self.matchTypes:
                    if to_port.DataType in types and from_port.DataType in types:
                        return True
                return False

        return True

    def set_property(self, name, value):
        super(AutoNode, self).set_property(name, value)
        self.set_port_type(name, type(value))

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
            if hasattr(current_port,"DataType"):
                if current_port.DataType is value_type:
                    return
            else:
                current_port.DataType = value_type

            current_port.border_color = rand_color(value_type)
            current_port.color = rand_color(value_type)
            conn_type = 'multi' if current_port.multi_connection() else 'single'
            dtat_type_name = value_type.__name__ if value_type else "all"
            current_port.view.setToolTip('{}: {} ({}) '.format(current_port.name(),dtat_type_name,conn_type))

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
        self._view._tooltip_disable(False)

    def _show_error(self,message):
        if not self._error:
            self.defaultColor = self.get_property("color")

        self._error = True
        self.set_property('color', self.errorColor)
        tooltip = '<b>{}</b>'.format(self.name())
        tooltip += ' <font color="red"><br>({})</br></font>'.format(message)
        tooltip += '<br/>{}<br/>'.format(self._view.type_)
        self._view.setToolTip(tooltip)

    def error(self,message = None):
        if message is None:
            return self._error

        self._show_error(message)

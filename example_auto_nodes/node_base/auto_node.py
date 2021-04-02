import copy
import time
import traceback

from Qt import QtCore, QtWidgets, QtGui

from NodeGraphQt import BaseNode, Port
from .utils import update_node_down_stream, get_data_type, CryptoColors


class AutoNode(BaseNode, QtCore.QObject):
    cooked = QtCore.Signal()

    def __init__(self, defaultInputType=None, defaultOutputType=None):
        super(AutoNode, self).__init__()
        QtCore.QObject.__init__(self)
        self._need_cook = True
        self._error = False
        self.matchTypes = [['float', 'int']]
        self.errorColor = (200, 50, 50)
        self.stopCookColor = (200, 200, 200)

        self.create_property('auto_cook', True)
        self.defaultValue = None
        self.defaultInputType = defaultInputType
        self.defaultOutputType = defaultOutputType

        self._cook_time = 0.0
        self._toolTip = self._setup_tool_tip()

        # effect
        self.color_effect = QtWidgets.QGraphicsColorizeEffect()
        self.color_effect.setStrength(0.7)
        self.color_effect.setEnabled(False)
        self.view.setGraphicsEffect(self.color_effect)

    @property
    def auto_cook(self):
        """
        Returns whether the node can update stream automatically.
        """

        return self.get_property('auto_cook')

    @auto_cook.setter
    def auto_cook(self, mode):
        """
        Set whether the node can update stream automatically.

        Args:
            mode(bool).
        """

        if mode is self.auto_cook:
            return

        self.model.set_property('auto_cook', mode)
        self.color_effect.setEnabled(not mode)
        if not mode:
            self.color_effect.setColor(QtGui.QColor(*self.stopCookColor))

    @property
    def cook_time(self):
        """
        Returns the last cooked time of the node.
        """

        return self._cook_time

    @cook_time.setter
    def cook_time(self, cook_time):
        """
        Set the last cooked time of the node.

        Args:
            cook_time(float).
        """

        self._cook_time = cook_time
        self._update_tool_tip()

    @property
    def has_error(self):
        """
        Returns whether the node has errors.
        """

        return self._error

    def update_stream(self, forceCook=False):
        """
        Update all down stream nodes.

        Args:
            forceCook(bool): if True, it will ignore the auto_cook and so on.
        """

        if not forceCook:
            if not self.auto_cook or not self._need_cook:
                return
            if self.graph is not None and not self.graph.auto_update:
                return
        update_node_down_stream(self)

    def get_data(self, port):
        """
        Get node data by port.
        Most time it will called by output nodes of the node.

        Args:
            port(Port).

        Returns:
            node data.
        """
        if self.disabled() and self.input_ports():
            out_ports = self.output_ports()
            if port in out_ports:
                idx = out_ports.index(port)
                max_idx = max(0, len(self.input_ports()) - 1)
                return self.get_input_data(min(idx, max_idx))

        return self.get_property(port.name())

    def get_input_data(self, port):
        """
        Get input data by input port name/index/object.

        Args:
            port(str/int/Port): input port name/index/object.
        """
        if type(port) is not Port:
            to_port = self.get_input(port)
        else:
            to_port = port
        if to_port is None:
            return copy.deepcopy(self.defaultValue)

        from_ports = to_port.connected_ports()
        if not from_ports:
            return copy.deepcopy(self.defaultValue)

        for from_port in from_ports:
            data = from_port.node().get_data(from_port)
            return copy.deepcopy(data)

    def cook(self):
        """
        The entry of the node evaluation.
        Most time we need to call this method instead of AutoNode.run'.
        """

        _tmp = self.auto_cook
        self.model.set_property('auto_cook', False)

        if self._error:
            self._close_error()

        _start_time = time.time()
        try:
            self.run()
        except:
            self.error(traceback.format_exc())

        self.model.set_property('auto_cook', _tmp)

        if self._error:
            return

        self.cook_time = time.time() - _start_time

        self.cooked.emit()

    def run(self):
        """
        Node evaluation logic.
        """

        pass

    def on_input_connected(self, to_port, from_port):
        if self.check_port_type(to_port, from_port):
            self.update_stream()
        else:
            self._need_cook = False
            to_port.disconnect_from(from_port)

    def on_input_disconnected(self, to_port, from_port):
        if not self._need_cook:
            self._need_cook = True
            return
        self.update_stream()

    def check_port_type(self, to_port, from_port):
        """
        Check whether the port_type of the to_port and from_type is matched.

        Args:
            to_port(Port).
            from_port(Port).

        Returns:
            bool.
        """

        if to_port.data_type != from_port.data_type:
            if to_port.data_type == 'NoneType' or from_port.data_type == 'NoneType':
                return True
            for types in self.matchTypes:
                if to_port.data_type in types and from_port.data_type in types:
                    return True
            return False

        return True

    def set_property(self, name, value):
        super(AutoNode, self).set_property(name, value)
        self.set_port_type(name, type(value).__name__)
        if name in self.model.custom_properties.keys():
            self.update_stream()

    def set_port_type(self, port, data_type: str):
        """
        Set the data_type of the port.

        Args:
            port(Port): the port to set the data_type.
            data_type(str): port new data_type.
        """

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
            if current_port.data_type == data_type:
                return
            else:
                current_port.data_type = data_type

            current_port.border_color = current_port.color = CryptoColors.get(data_type)
            conn_type = 'multi' if current_port.multi_connection() else 'single'
            current_port.view.setToolTip('{}: {} ({}) '.format(current_port.name(), data_type, conn_type))

    def add_input(self, name='input', data_type='', multi_input=False, display_name=True,
                  color=None, painter_func=None):
        new_port = super(AutoNode, self).add_input(name, multi_input, display_name,
                                                   color, data_type, painter_func)
        if data_type == '':
            data_type = self.defaultInputType
        self.set_port_type(new_port, get_data_type(data_type))
        return new_port

    def add_output(self, name='output', data_type='', multi_output=True, display_name=True,
                   color=None, painter_func=None):
        new_port = super(AutoNode, self).add_output(name, multi_output, display_name,
                                                    color, data_type, painter_func)
        if data_type == '':
            data_type = self.defaultOutputType
        self.set_port_type(new_port, get_data_type(data_type))
        return new_port

    def set_disabled(self, mode=False):
        super(AutoNode, self).set_disabled(mode)
        self.update_stream()

    def _close_error(self):
        """
        Close the node error.
        """

        self._error = False
        self.color_effect.setEnabled(False)
        self._update_tool_tip()

    def _update_tool_tip(self, message=None):
        """
        Update the node tooltip.

        Args:
            message(str): new node tooltip.
        """

        if message is None:
            tooltip = self._toolTip.format(self._cook_time)
        else:
            tooltip = '<b>{}</b>'.format(self.name())
            tooltip += message
            tooltip += '<br/>{}<br/>'.format(self._view.type_)
        self.view.setToolTip(tooltip)
        return tooltip

    def _setup_tool_tip(self):
        """
        Setup default node tooltip.

        Returns:
            str: new node tooltip.
        """
        tooltip = '<br> last cook used: {}s</br>'
        return self._update_tool_tip(tooltip)

    def error(self, message):
        """
        Change the node color and set error describe to the node tooltip.

        Args:
            message(str): the describe of the error.
        """

        self._error = True
        self.color_effect.setEnabled(True)
        self.color_effect.setColor(QtGui.QColor(*self.errorColor))
        tooltip = '<font color="red"><br>({})</br></font>'.format(message)
        self._update_tool_tip(tooltip)

    # def __del__(self):
    #     """
    #     Check gc.
    #     """
    #     print("Delete: ", self.name())


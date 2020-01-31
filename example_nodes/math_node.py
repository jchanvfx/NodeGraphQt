#!/usr/bin/python
# -*- coding: utf-8 -*-
import example_nodes.wrappers.math as math
import inspect
from functools import partial
from NodeGraphQt import BaseNode


class MathFunctionsNode(BaseNode):
    """
    Math functions node.
    """

    # set a unique node identifier.
    __identifier__ = 'Math'

    # set the initial default node name.
    NODE_NAME = 'Math Functions'

    mathFuncs = [func for func in dir(math) if not func.startswith('_')]

    def __init__(self):
        super(MathFunctionsNode, self).__init__()
        self.set_color(25, 58, 51)
        self.add_combo_menu('funcs', 'Functions', items=self.mathFuncs,
                            tab='widgets')

        # switch math function type
        self.view.widgets['funcs'].value_changed.connect(self.addFunction)
        self.view.widgets['funcs'].value_changed.connect(self.update_streams)
        self.add_output('output')
        self.create_property('output', None)
        self.trigger_type = 'no_inPorts'

        self.view.widgets['funcs'].widget.setCurrentIndex(2)

    def addFunction(self, prop, func):
        """
        Create inputs based on math functions arguments.
        """
        self.func = getattr(math, func)
        dataFunc = inspect.getfullargspec(self.func)

        for arg in dataFunc.args:
            if not self.has_property(arg):
                inPort = self.add_input(arg)
                inPort.trigger = True
                self.create_property(arg, None)

        for inPort in self._inputs:
            if inPort.name() in dataFunc.args:
                if not inPort.visible():
                    inPort.set_visible(True)
            else:
                inPort.set_visible(False)

    def run(self):
        """
        Evaluate all entries, pass them as arguments of the
        chosen mathematical function.
        """
        for to_port in self.input_ports():
            if to_port.visible() == False:
                continue
            from_ports = to_port.connected_ports()
            if not from_ports:
                raise Exception('Port %s not connected!' % to_port.name(),
                                to_port)

            for from_port in from_ports:
                from_port.node().run()
                data = from_port.node().get_property(from_port.name())
                self.set_property(to_port.name(), float(data))

        try:
            # Execute math function with arguments.
            data = self.func(*[self.get_property(inport.name()) for inport in self._inputs if inport.visible()])

            self.set_property('output', data)
        except KeyError as error:
            print("An input is missing! %s" % str(error))
        except TypeError as error:
            print("Error evaluating function: %s" % str(error))

    def on_input_connected(self, to_port, from_port):
        """Override node callback method."""
        self.set_property(to_port.name(), from_port.node().run())
        self.update_streams()

    def on_input_disconnected(self, to_port, from_port):
        """Override node callback method."""
        self.set_property('output', None)
        self.update_streams()

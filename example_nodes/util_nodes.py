#!/usr/bin/python
# -*- coding: utf-8 -*-
import inspect
from NodeGraphQt import BaseNode


class ObjectWrapperNode(BaseNode):
    """
    Take an object from the input port and wrappe it.
    """

    # set a unique node identifier.
    __identifier__ = 'Util'

    # set the initial default node name.
    NODE_NAME = 'Object Wrapper'

    def __init__(self):
        super(ObjectWrapperNode, self).__init__()
        self.selfPort = self.add_input('self')
        self.create_property('self', None)

    def buildNode(self):
        obj = self.get_property('self')
        if obj:
            self.set_name(obj.__class__.__name__.capitalize())
        else:
            self.set_name('Object Wrapper (None)')

        # switch math function type
        if 'methods' not in self.view.widgets:
            self.add_combo_menu('methods',
                                'Methods',
                                items=dir(obj),
                                tab='widgets')

            self.view.widgets['methods'].value_changed.connect(
                self.addFunction)
            self.view.widgets['methods'].value_changed.connect(
                self.update_streams)
            self.add_output('output')
            self.create_property('output', None)
        else:
            comboBox = self.view.widgets['methods'].widget
            comboBox.clear()
            comboBox.addItems(dir(obj))

    def addFunction(self, prop, func):
        """
        Create inputs based on math functions arguments.
        """
        self.funcName = func
        obj = self.get_property('self')
        func = getattr(obj, self.funcName)
        dataFunc = inspect.signature(func)

        for arg in dataFunc.args:
            if not self.has_property(arg):
                inPort = self.add_input(arg)
                self.create_property(arg, None)

        for inPort in self._inputs:
            if inPort.name() in dataFunc.args:
                if not inPort.visible():
                    inPort.set_visible(True)
            else:
                inPort.set_visible(False)

    def getSelf(self):
        for from_port in self.selfPort.connected_ports():
            return from_port.node().get_property(from_port.name())

    def run(self):
        """
        Evaluate all entries, pass them as arguments of the
        chosen mathematical function.
        """
        obj = self.getSelf()
        if not obj:
            return

        for to_port in self.input_ports():
            if to_port.visible() == False:
                continue

            from_ports = to_port.connected_ports()
            if not from_ports:
                raise Exception('Port %s not connected!' % to_port.name(),
                                to_port)

            for from_port in from_ports:
                if from_port.name() == 'self':
                    obj = from_port.node().get_property(from_port.name())
                    continue
                from_port.node().run()
                data = from_port.node().get_property(from_port.name())
                self.set_property(to_port.name(), data)

        self.func = getattr(obj, self.funcName)

        try:
            # Execute math function with arguments.
            data = self.func(*[
                self.get_property(inport.name()) for inport in self._inputs
                if inport.visible() and inport.name() != 'self'
            ])

            self.set_property('output', data)
        except KeyError as error:
            print("An input is missing! %s" % str(error))
        except TypeError as error:
            print("Error evaluating function: %s" % str(error))

    def on_input_connected(self, to_port, from_port):
        """Override node callback method."""
        from_port.node().run()
        outValue = from_port.node().get_property(from_port.name())
        self.set_property(to_port.name(), outValue)

        if to_port.name() == 'self':
            self.buildNode()
        self.update_streams()

    def on_input_disconnected(self, to_port, from_port):
        """Override node callback method."""
        self.set_property('self', None)
        self.set_property('output', None)
        comboBox = self.view.widgets['methods'].widget
        comboBox.clear()
        self.update_streams()

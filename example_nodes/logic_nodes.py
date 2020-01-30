from NodeGraphQt import BaseNode, QtCore


class IfNode(BaseNode):
    """
    if node.
    """

    __identifier__ = 'Logics'
    NODE_NAME = 'If'

    def __init__(self):
        super(IfNode, self).__init__()
        self.condition = self.add_input('condition')
        self._then = self.add_input('then')
        self._else = self.add_input('else')
        self.add_output('out')
        self.create_property('out',  None)

    def run(self):
        for port in self.condition.connected_ports():
            port.node().run()
            if port.node().get_property(port.name()):
                result = self._then
            else:
                result = self._else

        for port in result.connected_ports():
            port.node().run()
            self.set_property('out', port.node().get_property(port.name()))
            break

    def on_input_connected(self, to_port, from_port):
        """Override node callback method."""
        from_port.node().run()
        self.set_property(to_port.name(), from_port.node().get_property(from_port.name()))
        self.update_streams()

    def on_input_disconnected(self, to_port, from_port):
        """Override node callback method."""
        self.set_property('out', None)


class BooleanNode(BaseNode):
    """
    Boolean Logic funtions node.
    """

    __identifier__ = 'Logics'

    NODE_NAME = 'Boolean'

    logics = {'and': 'a and b',
              'or': 'a or b',
              'xor': '(not a and b) or (a and not b)',
              'not': 'not a'}

    def __init__(self):
        super(BooleanNode, self).__init__()
        self.a = self.add_input('a')
        self.b = self.add_input('b')
        self.add_output('out')
        self.create_property('out', None)
        self.add_combo_menu('funcs',
                            'Functions',
                            items=list(self.logics.keys()),
                            tab='widgets')

        self.func = self.logics['and']
        # switch math function type
        self.view.widgets['funcs'].value_changed.connect(self.addFunction)
        self.view.widgets['funcs'].value_changed.connect(self.update_streams)

    def addFunction(self, prop, func):
        """
        Create inputs based on math functions arguments.
        """
        self.func = self.logics[func]
        if self.b.visible() and not 'b' in self.func:
            self.b.set_visible(False)
        elif not self.b.visible():
            self.b.set_visible(True)

    def run(self):
        a = None
        b = None

        for port in self.a.connected_ports():
            port.node().run()
            a = port.node().get_property(port.name())

        for port in self.b.connected_ports():
            port.node().run()
            b = port.node().get_property(port.name())

        if a is None or (b is None and 'b' in self.func):
            raise Exception("No inputs!")

        self.set_property('out', eval(self.func))

    def on_input_connected(self, to_port, from_port):
        """Override node callback method."""
        from_port.node().run()
        result = from_port.node().get_property(from_port.name())
        self.set_property(to_port.name(), result)
        self.update_streams()

    def on_input_disconnected(self, to_port, from_port):
        """Override node callback method."""
        self.set_property('out', None)

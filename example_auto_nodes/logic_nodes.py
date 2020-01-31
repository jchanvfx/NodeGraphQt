from .basic_nodes import AutoNode


class IfNode(AutoNode):
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
        self.create_property('out', None)

    def run(self):
        if self.getInputData(self.condition):
            result = self.getInputData(self._then)
        else:
            result = self.getInputData(self._else)

        self.set_property('out', result)


class BooleanNode(AutoNode):
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
        self.a = self.add_input('a', bool)
        self.b = self.add_input('b', bool)
        self.add_output('out', bool)
        self.create_property('out', None)
        self.add_combo_menu('funcs',
                            'Functions',
                            items=list(self.logics.keys()),
                            tab='widgets')

        self.func = self.logics['and']
        # switch math function type
        self.view.widgets['funcs'].value_changed.connect(self.addFunction)

    def addFunction(self, prop, func):
        """
        Create inputs based on math functions arguments.
        """
        self.func = self.logics[func]
        if self.b.visible() and not 'b' in self.func:
            self.b.set_visible(False)
        elif not self.b.visible():
            self.b.set_visible(True)
        self.cook()

    def run(self):
        a = self.getInputData(self.a)
        b = self.getInputData(self.b)

        if a is None or (b is None and 'b' in self.func):
            self.error("No inputs!")
            return

        self.set_property('out', eval(self.func))

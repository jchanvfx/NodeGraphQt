#!/usr/bin/python
# -*- coding: utf-8 -*-
import math
import inspect
from functools import partial

# add basic math functions to math library
math.add = lambda x, y: x + y
math.sub = lambda x, y: x - y
math.mul = lambda x, y: x * y
math.div = lambda x, y: x / y

# Transform float to functions
for constant in ['pi', 'e', 'tau', 'inf', 'nan']:
    setattr(math, constant, partial(lambda x: x, getattr(math, constant)))

from NodeGraphQt import BaseNode
from .node_base.auto_node import AutoNode

class MathFunctionsNode(AutoNode):
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

        self.defaultValue = 0.0
        # switch math function type
        self.view.widgets['funcs'].value_changed.connect(self.addFunction)
        self.view.widgets['funcs'].value_changed.connect(self.cook)
        self.add_output('output')
        self.create_property('output', None)

        self.view.widgets['funcs'].widget.setCurrentIndex(2)

    def addFunction(self, prop, func):
        """
        Create inputs based on math functions arguments.
        """
        self.func = getattr(math, func)
        dataFunc = inspect.getfullargspec(self.func)

        for arg in dataFunc.args:
            if arg not in self.inputs().keys():
                inPort = self.add_input(arg,float)

        for inPort in self.input_ports():
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
        args = []
        for port in self.input_ports():
            if not port.visible():
                continue
            data = self.getInputData(port)
            if data and (type(data) is float or type(data) is int):
                args.append(data)
            else:
                args.append(0)
        try:
            # Execute math function with arguments.
            data = self.func(*args)

            self.set_property('output', data)
        except KeyError as error:
            self.error("An input is missing! %s" % str(error))
        except TypeError as error:
            self.error("Error evaluating function: %s" % str(error))
        except ValueError as error:
            self.error("Error input data type: %s" % str(error))
        except Exception as error:
            self.error("Error : %s" % str(error))

class VectorValue(AutoNode):
    __identifier__ = 'Math'
    NODE_NAME = 'Vector'

    def __init__(self):
        super(VectorValue, self).__init__()
        value = [0.0, 0.0, 0.0]

        self.add_output('out',list)
        self.create_property("out", value)

        self.add_float_input('0', 'X', value=value[0], tab='widgets')
        self.view.widgets['0'].value_changed.connect(lambda: self.updateValue(0))

        self.add_float_input('1', 'Y', value=value[1], tab='widgets')
        self.view.widgets['1'].value_changed.connect(lambda: self.updateValue(1))

        self.add_float_input('2', 'Z', value=value[2], tab='widgets')
        self.view.widgets['2'].value_changed.connect(lambda: self.updateValue(2))

        self.defaultValue = value

    def updateValue(self, index):
        self.get_property("out")[index] = self.get_property(str(index))
        self.cook()


class VectorSplit(AutoNode):
    __identifier__ = 'Math'
    NODE_NAME = 'Vector Split'

    def __init__(self):
        super(VectorSplit, self).__init__()
        self.defaultValue = [0.0, 0.0, 0.0]

        self.add_output('x')
        self.create_property("x", self.defaultValue[0])
        self.add_output('y')
        self.create_property("y", self.defaultValue[1])
        self.add_output('z')
        self.create_property("z", self.defaultValue[2])

        self.add_input("in vector",list)



    def run(self):
        value = self.getInputData(0)
        self.set_property("x", value[0])
        self.set_property("y", value[1])
        self.set_property("z", value[2])


class VectorMaker(AutoNode):
    __identifier__ = 'Math'
    NODE_NAME = 'Vector Maker'

    def __init__(self):
        super(VectorMaker, self).__init__()

        self.add_output('out')
        self.create_property("out", [0, 0, 0])

        self.add_input("x",float)
        self.add_input("y",float)
        self.add_input("z",float)

        self.defaultValue = 0.0

    def run(self):
        self.set_property("out", [self.getInputData(0), self.getInputData(1), self.getInputData(2)])

#!/usr/bin/python
# -*- coding: utf-8 -*-
from .node_base.auto_node import AutoNode


class VectorValue(AutoNode):
    """
    Create a basic vector data
    """

    __identifier__ = 'Data'
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
    """
    Splict a vector to x,y,z
    """

    __identifier__ = 'Data'
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
    """
    Create a vector by three float value
    """

    __identifier__ = 'Data'
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


class DataConvect(AutoNode):
    """
    Create a vector by three float value
    """

    __identifier__ = 'Data'
    NODE_NAME = 'Data Convect'

    def __init__(self):
        super(DataConvect, self).__init__()

        self.add_output('out')
        self.create_property("out",None)
        self.add_input("in data")

        items = ["all to int"]
        items.append("all to float")
        items.append("all to string")
        items.append("eval string")
        self.add_combo_menu('method', 'Method', items=items, tab='widgets')
        self.view.widgets['method'].value_changed.connect(self.cook)

    def run(self):
        method = self.get_property("method")
        try:
            if method == "all to int":
                data = int(self.getInputData(0))
            elif method == "all to float":
                data = float(self.getInputData(0))
            elif method == "all to string":
                data = str(self.getInputData(0))
            elif method == "eval string":
                data = eval(self.getInputData(0))
            self.set_property("out", data)
        except Exception as error:
            self.error(error)

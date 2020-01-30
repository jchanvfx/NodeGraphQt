#!/usr/bin/python
# -*- coding: utf-8 -*-
from .node_base.auto_node import AutoNode


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
        items.append("all to list")
        self.add_combo_menu('method', 'Method', items=items)

    def run(self):
        method = self.get_property("method")
        try:
            if method == "all to int":
                data = int(float(self.getInputData(0)))
            elif method == "all to float":
                data = float(self.getInputData(0))
            elif method == "all to string":
                data = str(self.getInputData(0))
            elif method == "eval string":
                data = eval(self.getInputData(0))
            elif method == "all to list":
                data = list(self.getInputData(0))
            self.set_property("out", data)
        except Exception as error:
            self.error(error)

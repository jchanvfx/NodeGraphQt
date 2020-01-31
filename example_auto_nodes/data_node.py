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

        self.add_output('x')
        self.create_property("x", 0.0)
        self.add_output('y')
        self.create_property("y", 0.0)
        self.add_output('z')
        self.create_property("z", 0.0)
        self.add_output('w')
        self.create_property("w", 0.0)

        self.add_input("in vector", list)
        self.map = {0: "x", 1: "y", 2: "z", 3: "w"}

    def run(self):
        value = self.getInputData(0)
        if type(value) is not list:
            self.error("Input data not list")
        for index, data in enumerate(value):
            if index > 3:
                return
            self.set_property(self.map[index], data)


class VectorMaker(AutoNode):
    """
    Create a vector by three float value
    """

    __identifier__ = 'Data'
    NODE_NAME = 'Vector Maker'

    def __init__(self):
        super(VectorMaker, self).__init__()

        self.add_output('out', list)
        self.create_property("out",None)

        self.add_input("x", float)
        self.add_input("y", float)
        self.add_input("z", float)
        self.add_input("w", float)

    def run(self):
        result = []
        for i in range(4):
            data = self.getInputData(i)
            if data is not None:
                result.append(data)

        self.set_property("out", result)


class DataConvect(AutoNode):
    """
    Create a vector by three float value
    """

    __identifier__ = 'Data'
    NODE_NAME = 'Data Convect'

    def __init__(self):
        super(DataConvect, self).__init__()

        self.add_output('out')
        self.create_property("out", None)
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

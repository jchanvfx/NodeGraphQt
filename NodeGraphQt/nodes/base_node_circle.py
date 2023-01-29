#!/usr/bin/python
from NodeGraphQt.nodes.base_node import BaseNode
from NodeGraphQt.qgraphics.node_circle import CircleNodeItem


class BaseNodeCircle(BaseNode):

    NODE_NAME = 'Circle Node'

    def __init__(self, qgraphics_item=None):
        super(BaseNodeCircle, self).__init__(qgraphics_item or CircleNodeItem)

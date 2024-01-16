#!/usr/bin/python
from NodeGraphQt.base.node import NodeObject
from NodeGraphQt.constants import NodePropWidgetEnum
from NodeGraphQt.qgraphics.node_backdrop import BackdropNodeItem


class BackdropNode(NodeObject):
    """
    The ``NodeGraphQt.BackdropNode`` class allows other node object to be
    nested inside, it's mainly good for grouping nodes together.

    .. inheritance-diagram:: NodeGraphQt.BackdropNode

    .. image:: ../_images/backdrop.png
        :width: 250px

    -
    """

    NODE_NAME = 'Backdrop'

    def __init__(self, qgraphics_views=None):
        super(BackdropNode, self).__init__(qgraphics_views or BackdropNodeItem)
        # override base default color.
        self.model.color = (5, 129, 138, 255)
        self.create_property('backdrop_text', '',
                             widget_type=NodePropWidgetEnum.QTEXT_EDIT.value,
                             tab='Backdrop')

    def on_backdrop_updated(self, update_prop, value=None):
        """
        Slot triggered by the "on_backdrop_updated" signal from
        the node graph.

        Args:
            update_prop (str): update property type.
            value (object): update value (optional)
        """
        if update_prop == 'sizer_mouse_release':
            self.graph.begin_undo('resized "{}"'.format(self.name()))
            self.set_property('width', value['width'])
            self.set_property('height', value['height'])
            self.set_pos(*value['pos'])
            self.graph.end_undo()
        elif update_prop == 'sizer_double_clicked':
            self.graph.begin_undo('"{}" auto resize'.format(self.name()))
            self.set_property('width', value['width'])
            self.set_property('height', value['height'])
            self.set_pos(*value['pos'])
            self.graph.end_undo()

    def auto_size(self):
        """
        Auto resize the backdrop node to fit around the intersecting nodes.
        """
        self.graph.begin_undo('"{}" auto resize'.format(self.name()))
        size = self.view.calc_backdrop_size()
        self.set_property('width', size['width'])
        self.set_property('height', size['height'])
        self.set_pos(*size['pos'])
        self.graph.end_undo()

    def wrap_nodes(self, nodes):
        """
        Set the backdrop size to fit around specified nodes.

        Args:
            nodes (list[NodeGraphQt.NodeObject]): list of nodes.
        """
        if not nodes:
            return
        self.graph.begin_undo('"{}" wrap nodes'.format(self.name()))
        size = self.view.calc_backdrop_size([n.view for n in nodes])
        self.set_property('width', size['width'])
        self.set_property('height', size['height'])
        self.set_pos(*size['pos'])
        self.graph.end_undo()

    def nodes(self):
        """
        Returns nodes wrapped within the backdrop node.

        Returns:
            list[NodeGraphQt.BaseNode]: list of node under the backdrop.
        """
        node_ids = [n.id for n in self.view.get_nodes()]
        return [self.graph.get_node_by_id(nid) for nid in node_ids]

    def set_text(self, text=''):
        """
        Sets the text to be displayed in the backdrop node.

        Args:
            text (str): text string.
        """
        self.set_property('backdrop_text', text)

    def text(self):
        """
        Returns the text on the backdrop node.

        Returns:
            str: text string.
        """
        return self.get_property('backdrop_text')

    def set_size(self, width, height):
        """
        Sets the backdrop size.

        Args:
            width (float): backdrop width size.
            height (float): backdrop height size.
        """
        if self.graph:
            self.graph.begin_undo('backdrop size')
            self.set_property('width', width)
            self.set_property('height', height)
            self.graph.end_undo()
            return
        self.view.width, self.view.height = width, height
        self.model.width, self.model.height = width, height

    def size(self):
        """
        Returns the current size of the node.

        Returns:
            tuple: node width, height
        """
        self.model.width = self.view.width
        self.model.height = self.view.height
        return self.model.width, self.model.height

    def inputs(self):
        # required function but unused for the backdrop node.
        return

    def outputs(self):
        # required function but unused for the backdrop node.
        return

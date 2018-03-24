#!/usr/bin/python


class _NodeManager(object):
    """
    Node manager that stores all the node types.
    """

    def __init__(self):
        self._aliases = {}
        self._names = {}
        self._nodes = {}

    @property
    def names(self):
        return self._names

    @property
    def aliases(self):
        return self._aliases

    @property
    def nodes(self):
        return self._nodes

    def create_node_instance(self, node_type):
        """
        create node class by the node type.

        Args:
            node_type (str):

        Returns:
            NodeGraphQt.Node: new node instance.
        """
        NodeInstance = self._nodes.get(node_type)
        return NodeInstance

    def register_node(self, node, alias=None):
        """
        register the node.

        Args:
            node (Node): node item
            alias (str): custom alias name for the node type.
        """
        if node is None:
            return

        name = node.NODE_NAME
        node_type = node.NODE_TYPE

        if node_type in self._nodes.keys():
            raise TypeError(
                'node type: {} already exists!'.format(node_type))
        self._nodes[node_type] = node

        if self._names.get(node_type):
            raise NameError(
                'node name: {} already exists!'.format(name))
        self._names[name] = node_type

        if alias:
            if self._aliases.get(alias):
                raise NameError(
                    'node alias: {} already exists!'.format(alias))
            self._aliases[alias] = node_type


NodeManager = _NodeManager()

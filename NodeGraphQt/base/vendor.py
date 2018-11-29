#!/usr/bin/python


class NodeVendor(object):
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

    def create_node_instance(self, node_type=None, alias=None):
        """
        create node class by the node type identifier or alias.

        Args:
            node_type (str): node type.
            alias (str): alias name (optional).

        Returns:
            NodeGraphQt.Node: new node instance object.
        """
        if alias and self.aliases.get(alias):
            node_type = self.aliases[alias]

        NodeInstance = self._nodes.get(node_type)
        if not NodeInstance:
            print('can\'t find node type {}'.format(node_type))
        return NodeInstance

    def register_node(self, node, alias=None):
        """
        register the node.

        Args:
            node (Node): node item
            alias (str): custom alias for the node (optional).
        """
        if node is None:
            return

        name = node.NODE_NAME
        node_type = node.type

        if self._nodes.get(node_type):
            raise AssertionError(
                'Node: {} already exists! '
                'Please specify a new plugin class name or identifier.'
                .format(node_type))
        self._nodes[node_type] = node

        if self._names.get(node_type):
            raise AssertionError(
                'Node Name: {} already exists!'
                'Please specify a new node name for node: {}'
                .format(name, node_type))
        self._names[name] = node_type

        if alias:
            if self._aliases.get(alias):
                raise AssertionError(
                    'Node Alias: {} already taken!'.format(alias))
            self._aliases[alias] = node_type
            
    def clear_registered_nodes(self):
        """
        clear out registered nodes, to prevent conflicts on reset.
        """
        self._nodes.clear()
        self._names.clear()
        self._aliases.clear()

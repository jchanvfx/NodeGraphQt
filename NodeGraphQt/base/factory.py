#!/usr/bin/python

from NodeGraphQt.errors import NodeRegistrationError


class NodeFactory(object):
    """
    Node factory that stores all the node types.
    """

    __aliases = {}
    __names = {}
    __nodes = {}

    @property
    def names(self):
        return self.__names

    @property
    def aliases(self):
        return self.__aliases

    @property
    def nodes(self):
        return self.__nodes

    def create_node_instance(self, node_type=None, alias=None):
        """
        create node class by the node type identifier or alias.

        Args:
            node_type (str): node type.
            alias (str): alias name (optional).

        Returns:
            NodeGraphQt.Node: new node class object.
        """
        if alias and self.aliases.get(alias):
            node_type = self.aliases[alias]

        NodeClass = self.__nodes.get(node_type)
        if not NodeClass:
            print('can\'t find node type {}'.format(node_type))
        return NodeClass

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
        node_type = node.type_

        if self.__nodes.get(node_type):
            raise NodeRegistrationError(
                'id "{}" already registered! '
                'Please specify a new plugin class name or __identifier__.'
                .format(node_type))
        self.__nodes[node_type] = node

        if self.__names.get(node_type):
            raise NodeRegistrationError(
                'Node Name: {} already exists!'
                'Please specify a new node name for node: {}'
                .format(name, node_type))
        self.__names[name] = node_type

        if alias:
            if self.__aliases.get(alias):
                raise NodeRegistrationError(
                    'Alias: "{}" already registered to "{}"'
                    .format(alias, self.__aliases.get(alias))
                )
            self.__aliases[alias] = node_type
            
    def clear_registered_nodes(self):
        """
        clear out registered nodes, to prevent conflicts on reset.
        """
        self.__nodes.clear()
        self.__names.clear()
        self.__aliases.clear()

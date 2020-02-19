#!/usr/bin/python

from ..errors import NodeRegistrationError


class NodeFactory(object):
    """
    Node factory that stores all the node types.
    """

    __aliases = {}
    __names = {}
    __nodes = {}

    @property
    def names(self):
        """
        Return all currently registered node type identifiers.

        Returns:
            dict: key=<node name, value=node_type
        """
        return self.__names

    @property
    def aliases(self):
        """
        Return aliases assigned to the node types.

        Returns:
            dict: key=alias, value=node type
        """
        return self.__aliases

    @property
    def nodes(self):
        """
        Return all registered nodes.

        Returns:
            dict: key=node identifier, value=node class
        """
        return self.__nodes

    def create_node_instance(self, node_type=None, alias=None):
        """
        create node class by the node type identifier or alias.

        Args:
            node_type (str): node type.
            alias (str): alias name (optional).

        Returns:
            NodeGraphQt.BaseNode: new node class object.
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
            alias (str): custom alias for the node identifier (optional).
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

        if self.__names.get(name):
            self.__names[name].append(node_type)
        else:
            self.__names[name] = [node_type]

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

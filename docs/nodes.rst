Nodes
*****


NodeObject
==========

**Inherited by:** :class:`NodeGraphQt.BaseNode`, :class:`NodeGraphQt.BackdropNode`

The ``NodeGraphQt.NodeObject`` class is the main base class that all nodes inherit from.

----

.. autoclass:: NodeGraphQt.NodeObject
    :members:
    :exclude-members: model, NODE_NAME

Attributes

.. autoattribute:: NodeGraphQt.NodeObject.__identifier__
.. autoattribute:: NodeGraphQt.NodeObject.NODE_NAME


BaseNode
========

**Inherited from:** :class:`NodeGraphQt.NodeObject`

The ``NodeGraphQt.BaseNode`` class is the base class for nodes that allows port connections from one node to another.


.. image:: _images/node.png
    :width: 250px

----

.. autoclass:: NodeGraphQt.BaseNode
    :members:
    :exclude-members: update_model


BackdropNode
============

**Inherited from:** :class:`NodeGraphQt.NodeObject`

The ``NodeGraphQt.BackdropNode`` class allows other node object to be nested inside, it's mainly good for grouping nodes together.

.. image:: _images/backdrop.png
    :width: 250px

----

.. autoclass:: NodeGraphQt.BackdropNode
    :members:


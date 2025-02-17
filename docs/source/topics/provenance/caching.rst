.. _topics:provenance:caching:

===================
Caching and hashing
===================

This section covers the more general considerations of the hashing/caching mechanism.
For a more practical guide on how to enable and disable this feature, please visit the corresponding :ref:`how-to section <how-to:run-codes:caching>`.
If you want to know more about how the internal design of the mechanism is implemented, you can check the :ref:`internals section <internal_architecture:engine:caching>` instead.


.. _topics:provenance:caching:hashing:

How are nodes hashed
--------------------

*Hashing* is turned on by default, i.e., all nodes in AiiDA are hashed.
This means that even when you enable caching once you have already completed a number of calculations, those calculations can still be used retro-actively by the caching mechanism since their hashes have been computed.

The hash of a ``Data`` node is computed from:

* all attributes of the node, except the ``_updatable_attributes`` and ``_hash_ignored_attributes``
* the ``__version__`` of the package which defined the node class
* the content of the repository folder of the node
* the UUID of the computer, if the node is associated with one

The hash of a :class:`~aiida.orm.ProcessNode` includes, on top of this, the hashes of all of its input ``Data`` nodes.

Once a node is stored in the database, its hash is stored in the ``_aiida_hash`` extra, and this extra is used to find matching nodes.
If a node of the same class with the same hash already exists in the database, this is considered a cache match.
You can use the :meth:`~aiida.orm.nodes.Node.get_hash` method to check the hash of any node.
In order to figure out why a calculation is *not* being reused, the :meth:`~aiida.orm.nodes.Node._get_objects_to_hash` method may be useful:

.. code-block:: ipython

    In [5]: node = load_node(1234)

    In [6]: node.get_hash()
    Out[6]: '62eca804967c9428bdbc11c692b7b27a59bde258d9971668e19ccf13a5685eb8'

    In [7]: node._get_objects_to_hash()
    Out[7]:
    [
        '1.0.0',
        {
            'resources': {'num_machines': 2, 'default_mpiprocs_per_machine': 28},
            'parser_name': 'cp2k',
            'linkname_retrieved': 'retrieved'
        },
        <aiida.common.folders.Folder at 0x1171b9a20>,
        '6850dc88-0949-482e-bba6-8b11205aec11',
        {
            'code': 'f6bd65b9ca3a5f0cf7d299d9cfc3f403d32e361aa9bb8aaa5822472790eae432',
            'parameters': '2c20fdc49672c3505cebabacfb9b1258e71e7baae5940a80d25837bee0032b59',
            'structure': 'c0f1c1d1bbcfc7746dcf7d0d675904c62a5b1759d37db77b564948fa5a788769',
            'parent_calc_folder': 'e375178ceeffcde086546d3ddbce513e0527b5fa99993091b2837201ad96569c'
        }
    ]


.. _topics:provenance:caching:control-hashing:

Controlling hashing
-------------------

Data nodes
..........

The hashing of *Data nodes* can be customized both when implementing a new data node class and during runtime.

In the :py:class:`~aiida.orm.nodes.Node` subclass:

* Use the ``_hash_ignored_attributes`` to exclude a list of node attributes ``['attr1', 'attr2']`` from computing the hash.
* Include extra information in computing the hash by overriding the :meth:`~aiida.orm.nodes.Node._get_objects_to_hash` method.
  Use the ``super()`` method, and then append to the list of objects to hash.

You can also modify hashing behavior during runtime by passing a keyword argument to :meth:`~aiida.orm.nodes.Node.get_hash`, which are forwarded to :meth:`~aiida.common.hashing.make_hash`.

Process nodes
.............

The hashing of *Process nodes* is fixed and can only be influenced indirectly via the hashes of their inputs.
For implementation details of the hashing mechanism for process nodes, see :ref:`here <internal_architecture:engine:caching>`.

.. _topics:provenance:caching:control-caching:

Controlling Caching
-------------------

In the caching mechanism, there are two different types of roles played by the nodes: the node that is currently being stored is called the `target`, and the nodes already stored in the database that are considered to be equivalent are referred to as a `source`.

Targets
.......

Controlling what nodes will look in the database for existing equivalents when being stored is done on the class level.
Section :ref:`how-to:run-codes:caching:configure` explains how this can be controlled globally through the profile configuration, or locally through context managers.

Sources
.......

When a node is being stored (the `target`) and caching is enabled for its node class (see section above), a valid cache `source` is obtained through the method :meth:`~aiida.orm.nodes.node.Node._get_same_node`.
This method calls the iterator :meth:`~aiida.orm.nodes.node.Node._iter_all_same_nodes` and takes the first one it returns if there are any.
To find the list of `source` nodes that are equivalent to the `target` that is being stored, :meth:`~aiida.orm.nodes.node.Node._iter_all_same_nodes` performs the following steps:

 1. It queries the database for all nodes that have the same hash as the `target` node.
 2. From the result, only those nodes are returned where the property :meth:`~aiida.orm.nodes.node.Node.is_valid_cache` returns ``True``.

The property :meth:`~aiida.orm.nodes.node.Node.is_valid_cache` therefore allows to control whether a stored node can be used as a `source` in the caching mechanism.
By default, for all nodes, the property returns ``True``.
However, this can be changed on a per-node basis, by setting it to ``False``

.. code-block:: python

    node = load_node(<IDENTIFIER>)
    node.is_valid_cache = False

Setting the property to ``False``, will cause an extra to be stored on the node in the database, such that even when it is loaded at a later point in time, ``is_valid_cache`` returns ``False``.

.. code-block:: python

    node = load_node(<IDENTIFIER>)
    assert node.is_valid_cache is False

Through this method, it is possible to guarantee that individual nodes are never used as a `source` for caching.

The :class:`~aiida.engine.processes.process.Process` class overrides the :meth:`~aiida.orm.nodes.node.Node.is_valid_cache` property to give more fine-grained control on process nodes as caching sources.
If either :meth:`~aiida.orm.nodes.node.Node.is_valid_cache` of the base class or :meth:`~aiida.orm.nodes.process.process.ProcessNode.is_finished` returns ``False``, the process node is not a valid source.
Likewise, if the process class cannot be loaded from the node, through the :meth:`~aiida.orm.nodes.process.process.ProcessNode.process_class`, the node is not a valid caching source.
Finally, if the associated process class implements the :meth:`~aiida.engine.processes.process.Process.is_valid_cache` method, it is called, passing the node as an argument.
If that returns ``True``, the node is considered to be a valid caching source.

The :meth:`~aiida.engine.processes.process.Process.is_valid_cache` is implemented on the :class:`~aiida.engine.processes.process.Process` class.
It will check whether the exit code that is set on the node, if any, has the keyword argument ``invalidates_cache`` set to ``True``, in which case the property will return ``False`` indicating the node is not a valid caching source.
Whether an exit code invalidates the cache, is controlled with the ``invalidates_cache`` argument when it is defined on the process spec through the :meth:`spec.exit_code <aiida.engine.processes.process_spec.ProcessSpec.exit_code>` method.

.. warning::

    Process plugins can override the :meth:`~aiida.engine.processes.process.Process.is_valid_cache` method, to further control how nodes are considered valid caching sources.
    When doing so, make sure to call :meth:`super().is_valid_cache(node) <aiida.engine.processes.process.Process.is_valid_cache>` and respect its output: if it is `False`, your implementation should also return `False`.
    If you do not comply with this, the ``invalidates_cache`` keyword on exit codes will no longer work.


.. _topics:provenance:caching:limitations:

Limitations and Guidelines
--------------------------

#. Workflow nodes are not cached.
   In the current design this follows from the requirement that the provenance graph be independent of whether caching is enabled or not:

   * **Calculation nodes:** Calculation nodes can have data inputs and create new data nodes as outputs.
     In order to make it look as if a cloned calculation produced its own outputs, the output nodes are copied and linked as well.
   * **Workflow nodes:** Workflows differ from calculations in that they can *return* an input node or an output node created by a calculation.
     Since caching does not care about the *identity* of input nodes but only their *content*, it is not straightforward to figure out which node to return in a cached workflow.

   This limitation has typically no significant impact since the runtime of AiiDA work chains is commonly dominated by expensive calculations.

#. The caching mechanism for calculations *should* trigger only when the inputs and the calculation to be performed are exactly the same.
   While AiiDA's hashes include the version of the Python package containing the calculation/data classes, it cannot detect cases where the underlying Python code was changed without increasing the version number.
   Another scenario that can lead to an erroneous cache hit is if the parser and calculation are not implemented as part of the same Python package, because the calculation nodes store only the name, but not the version of the used parser.

#. Note that while caching saves unnecessary computations, it does not save disk space: the output nodes of the cached calculation are full copies of the original outputs.

#. Finally, When modifying the hashing/caching behaviour of your classes, keep in mind that cache matches can go wrong in two ways:

   * False negatives, where two nodes *should* have the same hash but do not
   * False positives, where two different nodes get the same hash by mistake

   False negatives are **highly preferrable** because they only increase the runtime of your calculations, while false positives can lead to wrong results.

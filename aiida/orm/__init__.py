# -*- coding: utf-8 -*-
from aiida.orm.node import Node
from aiida.orm.calculation import Calculation
from aiida.orm.calculation.job import JobCalculation
from aiida.orm.code import Code
from aiida.orm.data import Data
from aiida.orm.workflow import Workflow
from aiida.orm.computer import Computer
from aiida.orm.group import Group

__copyright__ = u"Copyright (c), 2015, ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE (Theory and Simulation of Materials (THEOS) and National Centre for Computational Design and Discovery of Novel Materials (NCCR MARVEL)), Switzerland and ROBERT BOSCH LLC, USA. All rights reserved."
__license__ = "MIT license, see LICENSE.txt file"
__version__ = "0.5.0"
__contributors__ = "Andrea Cepellotti, Andrius Merkys, Giovanni Pizzi, Nicolas Mounet"


def CalculationFactory(module, from_abstract=False):
    """
    Return a suitable JobCalculation subclass.
    
    :param module: a valid string recognized as a Calculation plugin
    :param from_abstract: A boolean. If False (default), actually look only
      to subclasses to JobCalculation, not to the base Calculation class.
      If True, check for valid strings for plugins of the Calculation base class.
    """
    from aiida.common.pluginloader import BaseFactory

    if from_abstract:
        return BaseFactory(module, Calculation, "aiida.orm.calculation")
    else:
        return BaseFactory(module, JobCalculation, "aiida.orm.calculation.job",
                           suffix="Calculation")


def DataFactory(module):
    """
    Return a suitable Data subclass.
    """
    from aiida.common.pluginloader import BaseFactory

    return BaseFactory(module, Data, "aiida.orm.data")


def WorkflowFactory(module):
    """
    Return a suitable Workflow subclass.
    """
    from aiida.common.pluginloader import BaseFactory

    return BaseFactory(module, Workflow, "aiida.workflows")


def load_node(node_id=None, pk=None, uuid=None, parent_class=None):
    """
    Return an AiiDA node given PK or UUID.

    :param node_id: PK (integer) or UUID (string) or a node
    :param pk: PK of a node
    :param uuid: UUID of a node
    :param parent_class: if specified, checks whether the node loaded is a 
        subclass of parent_class
    :return: an AiiDA node
    :raise ValueError: if none or more than one of parameters is supplied
        or type of node_id is neither string nor integer.
    :raise NotExistent: if the parent_class is specified 
        and no matching Node is found.
    """
    from aiida.orm.node import Node
    from aiida.common.exceptions import NotExistent
    
    if int(node_id is None) + int(pk is None) + int(uuid is None) == 3:
        raise ValueError("one of the parameters 'node_id', 'pk' and 'uuid' "
                         "has to be supplied")
    if int(node_id is None) + int(pk is None) + int(uuid is None) < 2:
        raise ValueError("only one of parameters 'node_id', 'pk' and 'uuid' "
                         "has to be supplied")
    loaded_node = None
    if node_id is not None:
        if isinstance(node_id, str) or isinstance(node_id, unicode):
            loaded_node = Node.get_subclass_from_uuid(node_id)
        elif isinstance(node_id, int):
            loaded_node = Node.get_subclass_from_pk(node_id)
        else:
            raise ValueError("'node_id' has to be either string, unicode or "
                             "integer, {} given".format(type(node_id)))
    if loaded_node is None:
        if pk is not None:
            loaded_node = Node.get_subclass_from_pk(pk)
        else:
            loaded_node = Node.get_subclass_from_uuid(uuid)

    if parent_class is not None:
        if not issubclass(parent_class, Node):
            raise ValueError("parent_class must be a subclass of Node")
        if not isinstance(loaded_node, parent_class):
            raise NotExistent('No node found as '
                              'subclass of {}'.format(parent_class))

    return loaded_node


def load_workflow(wf_id=None, pk=None, uuid=None):
    """
    Return an AiiDA workflow given PK or UUID.

    :param wf_id: PK (integer) or UUID (string) or a workflow
    :param pk: PK of a workflow
    :param uuid: UUID of a workflow
    :return: an AiiDA workflow
    :raises: ValueError if none or more than one of parameters is supplied
        or type of wf_id is neither string nor integer
    """
    if int(wf_id is None) + int(pk is None) + int(uuid is None) == 3:
        raise ValueError("one of the parameters 'wf_id', 'pk' and 'uuid' "
                         "has to be supplied")
    if int(wf_id is None) + int(pk is None) + int(uuid is None) < 2:
        raise ValueError("only one of parameters 'wf_id', 'pk' and 'uuid' "
                         "has to be supplied")
    if wf_id is not None:
        if isinstance(wf_id, str) or isinstance(wf_id, unicode):
            return Workflow.get_subclass_from_uuid(wf_id)
        elif isinstance(wf_id, int):
            return Workflow.get_subclass_from_pk(wf_id)
        else:
            raise ValueError("'wf_id' has to be either string, unicode or "
                             "integer, {} given".format(type(wf_id)))
    if pk is not None:
        return Workflow.get_subclass_from_pk(pk)
    else:
        return Workflow.get_subclass_from_uuid(uuid)

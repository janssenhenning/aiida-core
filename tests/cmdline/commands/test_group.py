# -*- coding: utf-8 -*-
###########################################################################
# Copyright (c), The AiiDA team. All rights reserved.                     #
# This file is part of the AiiDA code.                                    #
#                                                                         #
# The code is hosted on GitHub at https://github.com/aiidateam/aiida-core #
# For further information on the license, see the LICENSE.txt file        #
# For further information please visit http://www.aiida.net               #
###########################################################################
"""Tests for the `verdi group` command."""
from aiida import orm
from aiida.backends.testbase import AiidaTestCase
from aiida.cmdline.commands import cmd_group
from aiida.cmdline.utils.echo import ExitCode
from aiida.common import exceptions


class TestVerdiGroup(AiidaTestCase):
    """Tests for the `verdi group` command."""

    def setUp(self):
        """Create runner object to run tests."""
        from click.testing import CliRunner
        self.cli_runner = CliRunner()

        for group in ['dummygroup1', 'dummygroup2', 'dummygroup3', 'dummygroup4']:
            orm.Group(label=group).store()

    def tearDown(self):
        """Delete all created group objects."""
        for group in orm.Group.objects.all():
            orm.Group.objects.delete(group.pk)

    def test_help(self):
        """Tests help text for all group sub commands."""
        options = ['--help']

        # verdi group list
        result = self.cli_runner.invoke(cmd_group.group_list, options)
        self.assertIsNone(result.exception, result.output)
        self.assertIn('Usage', result.output)

        # verdi group create
        result = self.cli_runner.invoke(cmd_group.group_create, options)
        self.assertIsNone(result.exception, result.output)
        self.assertIn('Usage', result.output)

        # verdi group delete
        result = self.cli_runner.invoke(cmd_group.group_delete, options)
        self.assertIsNone(result.exception, result.output)
        self.assertIn('Usage', result.output)

        # verdi group relabel
        result = self.cli_runner.invoke(cmd_group.group_relabel, options)
        self.assertIsNone(result.exception, result.output)
        self.assertIn('Usage', result.output)

        # verdi group description
        result = self.cli_runner.invoke(cmd_group.group_description, options)
        self.assertIsNone(result.exception, result.output)
        self.assertIn('Usage', result.output)

        # verdi group addnodes
        result = self.cli_runner.invoke(cmd_group.group_add_nodes, options)
        self.assertIsNone(result.exception, result.output)
        self.assertIn('Usage', result.output)

        # verdi group removenodes
        result = self.cli_runner.invoke(cmd_group.group_remove_nodes, options)
        self.assertIsNone(result.exception, result.output)
        self.assertIn('Usage', result.output)

        # verdi group show
        result = self.cli_runner.invoke(cmd_group.group_show, options)
        self.assertIsNone(result.exception, result.output)
        self.assertIn('Usage', result.output)

        # verdi group copy
        result = self.cli_runner.invoke(cmd_group.group_copy, options)
        self.assertIsNone(result.exception, result.output)
        self.assertIn('Usage', result.output)

    def test_create(self):
        """Test `verdi group create` command."""
        result = self.cli_runner.invoke(cmd_group.group_create, ['dummygroup5'])
        self.assertClickResultNoException(result)

        # check if newly added group in present in list
        result = self.cli_runner.invoke(cmd_group.group_list)
        self.assertClickResultNoException(result)

        self.assertIn('dummygroup5', result.output)

    def test_list(self):
        """Test `verdi group list` command."""
        result = self.cli_runner.invoke(cmd_group.group_list)
        self.assertClickResultNoException(result)

        for grp in ['dummygroup1', 'dummygroup2']:
            self.assertIn(grp, result.output)

    def test_list_order(self):
        """Test `verdi group list` command with ordering options."""
        orm.Group(label='agroup').store()

        options = []
        result = self.cli_runner.invoke(cmd_group.group_list, options)
        self.assertClickResultNoException(result)
        group_ordering = [l.split()[1] for l in result.output.split('\n')[3:] if l]
        self.assertEqual(['dummygroup1', 'dummygroup2', 'dummygroup3', 'dummygroup4', 'agroup'], group_ordering)

        options = ['--order-by', 'label']
        result = self.cli_runner.invoke(cmd_group.group_list, options)
        self.assertClickResultNoException(result)
        group_ordering = [l.split()[1] for l in result.output.split('\n')[3:] if l]
        self.assertEqual(['agroup', 'dummygroup1', 'dummygroup2', 'dummygroup3', 'dummygroup4'], group_ordering)

        options = ['--order-by', 'id', '--order-direction', 'desc']
        result = self.cli_runner.invoke(cmd_group.group_list, options)
        self.assertClickResultNoException(result)
        group_ordering = [l.split()[1] for l in result.output.split('\n')[3:] if l]
        self.assertEqual(['agroup', 'dummygroup4', 'dummygroup3', 'dummygroup2', 'dummygroup1'], group_ordering)

    def test_copy(self):
        """Test `verdi group copy` command."""
        result = self.cli_runner.invoke(cmd_group.group_copy, ['dummygroup1', 'dummygroup2'])
        self.assertClickResultNoException(result)

        self.assertIn('Success', result.output)

    def test_delete(self):
        """Test `verdi group delete` command."""
        orm.Group(label='group_test_delete_01').store()
        orm.Group(label='group_test_delete_02').store()
        orm.Group(label='group_test_delete_03').store()

        # dry run
        result = self.cli_runner.invoke(cmd_group.group_delete, ['--dry-run', 'group_test_delete_01'])
        self.assertClickResultNoException(result)
        orm.load_group(label='group_test_delete_01')

        result = self.cli_runner.invoke(cmd_group.group_delete, ['--force', 'group_test_delete_01'])
        self.assertClickResultNoException(result)

        # Verify that removed group is not present in list
        result = self.cli_runner.invoke(cmd_group.group_list)
        self.assertClickResultNoException(result)
        self.assertNotIn('group_test_delete_01', result.output)

        node_01 = orm.CalculationNode().store()
        node_02 = orm.CalculationNode().store()
        node_pks = {node_01.pk, node_02.pk}

        # Add some nodes and then use `verdi group delete` to delete a group that contains nodes
        group = orm.load_group(label='group_test_delete_02')
        group.add_nodes([node_01, node_02])
        self.assertEqual(group.count(), 2)

        result = self.cli_runner.invoke(cmd_group.group_delete, ['--force', 'group_test_delete_02'])

        with self.assertRaises(exceptions.NotExistent):
            orm.load_group(label='group_test_delete_02')

        # check nodes still exist
        for pk in node_pks:
            orm.load_node(pk)

        # delete the group and the nodes it contains
        group = orm.load_group(label='group_test_delete_03')
        group.add_nodes([node_01, node_02])
        result = self.cli_runner.invoke(cmd_group.group_delete, ['--force', '--delete-nodes', 'group_test_delete_03'])
        self.assertClickResultNoException(result)

        # check group and nodes no longer exist
        with self.assertRaises(exceptions.NotExistent):
            orm.load_group(label='group_test_delete_03')
        for pk in node_pks:
            with self.assertRaises(exceptions.NotExistent):
                orm.load_node(pk)

    def test_show(self):
        """Test `verdi group show` command."""
        result = self.cli_runner.invoke(cmd_group.group_show, ['dummygroup1'])
        self.assertClickResultNoException(result)

        for grpline in [
            'Group label', 'dummygroup1', 'Group type_string', 'core', 'Group description', '<no description>'
        ]:
            self.assertIn(grpline, result.output)

    def test_show_limit(self):
        """Test `--limit` option of the `verdi group show` command."""
        label = 'test_group_limit'
        nodes = [orm.Data().store(), orm.Data().store()]
        group = orm.Group(label=label).store()
        group.add_nodes(nodes)

        # Default should include all nodes in the output
        result = self.cli_runner.invoke(cmd_group.group_show, [label])
        self.assertClickResultNoException(result)

        for node in nodes:
            self.assertIn(str(node.pk), result.output)

        # Repeat test with `limit=1`, use also the `--raw` option to only display nodes
        result = self.cli_runner.invoke(cmd_group.group_show, [label, '--limit', '1', '--raw'])
        self.assertClickResultNoException(result)

        # The current `verdi group show` does not support ordering so we cannot rely on that for now to test if only
        # one of the nodes is shown
        self.assertEqual(len(result.output.strip().split('\n')), 1)
        self.assertTrue(str(nodes[0].pk) in result.output or str(nodes[1].pk) in result.output)

        # Repeat test with `limit=1` but without the `--raw` flag as it has a different code path that is affected
        result = self.cli_runner.invoke(cmd_group.group_show, [label, '--limit', '1'])
        self.assertClickResultNoException(result)

        # Check that one, and only one pk appears in the output
        self.assertTrue(str(nodes[0].pk) in result.output or str(nodes[1].pk) in result.output)
        self.assertTrue(not (str(nodes[0].pk) in result.output and str(nodes[1].pk) in result.output))

    def test_description(self):
        """Test `verdi group description` command."""
        description = 'It is a new description'
        group = orm.load_group(label='dummygroup2')
        self.assertNotEqual(group.description, description)

        # Change the description of the group
        result = self.cli_runner.invoke(cmd_group.group_description, [group.label, description])
        self.assertClickResultNoException(result)
        self.assertEqual(group.description, description)

        # When no description argument is passed the command should just echo the current description
        result = self.cli_runner.invoke(cmd_group.group_description, [group.label])
        self.assertClickResultNoException(result)
        self.assertIn(description, result.output)

    def test_relabel(self):
        """Test `verdi group relabel` command."""
        result = self.cli_runner.invoke(cmd_group.group_relabel, ['dummygroup4', 'relabeled_group'])
        self.assertIsNone(result.exception, result.output)

        # check if group list command shows changed group name
        result = self.cli_runner.invoke(cmd_group.group_list)
        self.assertClickResultNoException(result)
        self.assertNotIn('dummygroup4', result.output)
        self.assertIn('relabeled_group', result.output)

    def test_add_remove_nodes(self):
        """Test `verdi group remove-nodes` command."""
        node_01 = orm.CalculationNode().store()
        node_02 = orm.CalculationNode().store()
        node_03 = orm.CalculationNode().store()

        result = self.cli_runner.invoke(cmd_group.group_add_nodes, ['--force', '--group=dummygroup1', node_01.uuid])
        self.assertClickResultNoException(result)

        # Check if node is added in group using group show command
        result = self.cli_runner.invoke(cmd_group.group_show, ['dummygroup1'])
        self.assertClickResultNoException(result)
        self.assertIn('CalculationNode', result.output)
        self.assertIn(str(node_01.pk), result.output)

        # Remove same node
        result = self.cli_runner.invoke(cmd_group.group_remove_nodes, ['--force', '--group=dummygroup1', node_01.uuid])
        self.assertIsNone(result.exception, result.output)

        # Check that the node is no longer in the group
        result = self.cli_runner.invoke(cmd_group.group_show, ['-r', 'dummygroup1'])
        self.assertClickResultNoException(result)
        self.assertNotIn('CalculationNode', result.output)
        self.assertNotIn(str(node_01.pk), result.output)

        # Add all three nodes and then use `verdi group remove-nodes --clear` to remove them all
        group = orm.load_group(label='dummygroup1')
        group.add_nodes([node_01, node_02, node_03])
        self.assertEqual(group.count(), 3)

        result = self.cli_runner.invoke(cmd_group.group_remove_nodes, ['--force', '--clear', '--group=dummygroup1'])
        self.assertClickResultNoException(result)
        self.assertEqual(group.count(), 0)

        # Try to remove node that isn't in the group
        result = self.cli_runner.invoke(cmd_group.group_remove_nodes, ['--group=dummygroup1', node_01.uuid])
        self.assertEqual(result.exit_code, ExitCode.CRITICAL)

        # Try to remove no nodes nor clear the group
        result = self.cli_runner.invoke(cmd_group.group_remove_nodes, ['--group=dummygroup1'])
        self.assertEqual(result.exit_code, ExitCode.CRITICAL)

        # Try to remove both nodes and clear the group
        result = self.cli_runner.invoke(cmd_group.group_remove_nodes, ['--group=dummygroup1', '--clear', node_01.uuid])
        self.assertEqual(result.exit_code, ExitCode.CRITICAL)

        # Add a node with confirmation
        result = self.cli_runner.invoke(cmd_group.group_add_nodes, ['--group=dummygroup1', node_01.uuid], input='y')
        self.assertEqual(group.count(), 1)

        # Try to remove two nodes, one that isn't in the group, but abort
        result = self.cli_runner.invoke(
            cmd_group.group_remove_nodes, ['--group=dummygroup1', node_01.uuid, node_02.uuid], input='N'
        )
        self.assertIn('Warning', result.output)
        self.assertEqual(group.count(), 1)

        # Try to clear all nodes from the group, but abort
        result = self.cli_runner.invoke(cmd_group.group_remove_nodes, ['--group=dummygroup1', '--clear'], input='N')
        self.assertIn('Are you sure you want to remove ALL', result.output)
        self.assertIn('Aborted', result.output)
        self.assertEqual(group.count(), 1)

    def test_move_nodes(self):
        """Test `verdi group move-nodes` command."""
        node_01 = orm.CalculationNode().store()
        node_02 = orm.Int(1).store()
        node_03 = orm.Bool(True).store()

        group1 = orm.load_group('dummygroup1')
        group2 = orm.load_group('dummygroup2')

        group1.add_nodes([node_01, node_02])

        # Moving the nodes to the same group
        result = self.cli_runner.invoke(
            cmd_group.group_move_nodes, ['-s', 'dummygroup1', '-t', 'dummygroup1', node_01.uuid, node_02.uuid]
        )
        self.assertIn('Source and target group are the same:', result.output)

        # Not specifying NODES or `--all`
        result = self.cli_runner.invoke(cmd_group.group_move_nodes, ['-s', 'dummygroup1', '-t', 'dummygroup2'])
        self.assertIn('Neither NODES or the `-a, --all` option was specified.', result.output)

        # Moving the nodes from the empty group
        result = self.cli_runner.invoke(
            cmd_group.group_move_nodes, ['-s', 'dummygroup2', '-t', 'dummygroup1', node_01.uuid, node_02.uuid]
        )
        self.assertIn('None of the specified nodes are in', result.output)

        # Move two nodes to the second dummy group, but specify a missing uuid
        result = self.cli_runner.invoke(
            cmd_group.group_move_nodes, ['-s', 'dummygroup1', '-t', 'dummygroup2', node_01.uuid, node_03.uuid]
        )
        self.assertIn(f'1 nodes with PK {{{node_03.pk}}} are not in', result.output)
        # Check that the node that is present is actually moved
        result = self.cli_runner.invoke(
            cmd_group.group_move_nodes,
            ['-f', '-s', 'dummygroup1', '-t', 'dummygroup2', node_01.uuid, node_03.uuid],
        )
        assert node_01 not in group1.nodes
        assert node_01 in group2.nodes

        # Add the first node back to the first group, and try to move it from the second one
        group1.add_nodes(node_01)
        result = self.cli_runner.invoke(
            cmd_group.group_move_nodes, ['-s', 'dummygroup2', '-t', 'dummygroup1', node_01.uuid]
        )
        self.assertIn(f'1 nodes with PK {{{node_01.pk}}} are already', result.output)
        # Check that it is still removed from the second group
        result = self.cli_runner.invoke(
            cmd_group.group_move_nodes,
            ['-f', '-s', 'dummygroup2', '-t', 'dummygroup1', node_01.uuid],
        )
        assert node_01 not in group2.nodes

        # Force move the two nodes to the second dummy group
        result = self.cli_runner.invoke(
            cmd_group.group_move_nodes, ['-f', '-s', 'dummygroup1', '-t', 'dummygroup2', node_01.uuid, node_02.uuid]
        )
        assert node_01 in group2.nodes
        assert node_02 in group2.nodes

        # Force move all nodes back to the first dummy group
        result = self.cli_runner.invoke(
            cmd_group.group_move_nodes, ['-f', '-s', 'dummygroup2', '-t', 'dummygroup1', '--all']
        )
        assert node_01 not in group2.nodes
        assert node_02 not in group2.nodes
        assert node_01 in group1.nodes
        assert node_02 in group1.nodes

    def test_copy_existing_group(self):
        """Test user is prompted to continue if destination group exists and is not empty"""
        source_label = 'source_copy_existing_group'
        dest_label = 'dest_copy_existing_group'

        # Create source group with nodes
        calc_s1 = orm.CalculationNode().store()
        calc_s2 = orm.CalculationNode().store()
        nodes_source_group = {str(node.uuid) for node in [calc_s1, calc_s2]}
        source_group = orm.Group(label=source_label).store()
        source_group.add_nodes([calc_s1, calc_s2])

        # Copy using `verdi group copy` - making sure all is successful
        options = [source_label, dest_label]
        result = self.cli_runner.invoke(cmd_group.group_copy, options)
        self.assertClickResultNoException(result)
        self.assertIn(
            f'Success: Nodes copied from {source_group} to {source_group.__class__.__name__}<{dest_label}>.',
            result.output, result.exception
        )

        # Check destination group exists with source group's nodes
        dest_group = orm.load_group(label=dest_label)
        self.assertEqual(dest_group.count(), 2)
        nodes_dest_group = {str(node.uuid) for node in dest_group.nodes}
        self.assertSetEqual(nodes_source_group, nodes_dest_group)

        # Copy again, making sure an abort error is raised, since no user input can be made and default is abort
        result = self.cli_runner.invoke(cmd_group.group_copy, options)
        self.assertIsNotNone(result.exception, result.output)
        self.assertIn(
            f'Warning: Destination {dest_group} already exists and is not empty.', result.output, result.exception
        )

        # Check destination group is unchanged
        dest_group = orm.load_group(label=dest_label)
        self.assertEqual(dest_group.count(), 2)
        nodes_dest_group = {str(node.uuid) for node in dest_group.nodes}
        self.assertSetEqual(nodes_source_group, nodes_dest_group)

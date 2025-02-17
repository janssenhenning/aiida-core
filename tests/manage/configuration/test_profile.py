# -*- coding: utf-8 -*-
###########################################################################
# Copyright (c), The AiiDA team. All rights reserved.                     #
# This file is part of the AiiDA code.                                    #
#                                                                         #
# The code is hosted on GitHub at https://github.com/aiidateam/aiida-core #
# For further information on the license, see the LICENSE.txt file        #
# For further information please visit http://www.aiida.net               #
###########################################################################
"""Tests for the Profile class."""

import os
import uuid

from aiida.backends.testbase import AiidaTestCase
from aiida.manage.configuration import Profile
from tests.utils.configuration import create_mock_profile


class TestProfile(AiidaTestCase):
    """Tests for the Profile class."""

    @classmethod
    def setUpClass(cls, *args, **kwargs):
        """Setup a mock profile."""
        super().setUpClass(*args, **kwargs)
        cls.profile_name = 'test_profile'
        cls.profile_dictionary = {
            'default_user_email': 'dummy@localhost',
            'storage': {
                'backend': 'psql_dos',
                'config': {
                    'database_engine': 'postgresql_psycopg2',
                    'database_name': cls.profile_name,
                    'database_port': '5432',
                    'database_hostname': 'localhost',
                    'database_username': 'user',
                    'database_password': 'pass',
                    'repository_uri': f"file:///{os.path.join('/some/path', f'repository_{cls.profile_name}')}",
                }
            },
            'process_control': {
                'backend': 'rabbitmq',
                'config': {
                    'broker_protocol': 'amqp',
                    'broker_username': 'guest',
                    'broker_password': 'guest',
                    'broker_host': 'localhost',
                    'broker_port': 5672,
                    'broker_virtual_host': '',
                }
            }
        }
        cls.profile = Profile(cls.profile_name, cls.profile_dictionary)

    def test_base_properties(self):
        """Test the basic properties of a Profile instance."""
        self.assertEqual(self.profile.name, self.profile_name)

        self.assertEqual(self.profile.storage_backend, 'psql_dos')
        self.assertEqual(self.profile.storage_config, self.profile_dictionary['storage']['config'])
        self.assertEqual(self.profile.process_control_backend, 'rabbitmq')
        self.assertEqual(self.profile.process_control_config, self.profile_dictionary['process_control']['config'])

        # Verify that the uuid property returns a valid UUID by attempting to construct an UUID instance from it
        uuid.UUID(self.profile.uuid)

        # Check that the default user email field is not None
        self.assertIsNotNone(self.profile.default_user_email)

        # The RabbitMQ prefix should contain the profile UUID
        self.assertIn(self.profile.uuid, self.profile.rmq_prefix)

    def test_is_test_profile(self):
        """Test that a profile whose name starts with `test_` is marked as a test profile."""
        profile_name = 'not_a_test_profile'
        profile = create_mock_profile(name=profile_name)

        # The one constructed in the setUpClass should be a test profile
        self.assertTrue(self.profile.is_test_profile)

        # The profile created here should *not* be a test profile
        self.assertFalse(profile.is_test_profile)

    def test_set_option(self):
        """Test the `set_option` method."""
        option_key = 'daemon.timeout'
        option_value_one = 999
        option_value_two = 666

        # Setting an option if it does not exist should work
        self.profile.set_option(option_key, option_value_one)
        self.assertEqual(self.profile.get_option(option_key), option_value_one)

        # Setting it again will override it by default
        self.profile.set_option(option_key, option_value_two)
        self.assertEqual(self.profile.get_option(option_key), option_value_two)

        # If we set override to False, it should not override, big surprise
        self.profile.set_option(option_key, option_value_one, override=False)
        self.assertEqual(self.profile.get_option(option_key), option_value_two)

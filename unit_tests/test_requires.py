
# Copyright 2021 Canonical Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import charms_openstack.test_utils as test_utils
import mock

import requires

TEST_IP = "10.10.10.10"
TEST_PORT = 3306


class TestRegisteredHooks(test_utils.TestRegisteredHooks):

    def test_hooks(self):
        defaults = []
        hook_set = {
            "when": {
                "joined": ("endpoint.{endpoint_name}.joined",),
            },
            "when_any": {
                "broken_or_departed": (
                    "endpoint.{endpoint_name}.departed",
                    "endpoint.{endpoint_name}.broken",
                ),
            }
        }
        # test that the hooks were registered
        self.registered_hooks_test_helper(requires, hook_set, defaults)


class TestMySQLMonitorRequires(test_utils.PatchHelper):

    def setUp(self):
        """Set up before each test."""
        super().setUp()
        self._patches = {}
        self._patches_start = {}
        self.patch_object(requires, "clear_flag")
        self.patch_object(requires, "set_flag")

        self.fake_unit = mock.MagicMock()
        self.fake_unit.unit_name = "mysql-innodb-cluster/0"

        self.fake_relation_id = "db-monitor:42"
        self.fake_relation = mock.MagicMock()
        self.fake_relation.relation_id = self.fake_relation_id
        self.fake_relation.units = [self.fake_unit]

        self.ep_name = "db-monitor"
        self.ep = requires.MySQLMonitorClient(
            self.ep_name, [self.fake_relation_id]
        )
        self.ep.relations[0] = self.fake_relation

    def tearDown(self):
        """Clean after each test."""
        self.ep = None
        for k, v in self._patches.items():
            v.stop()
            setattr(self, k, None)
        self._patches = None
        self._patches_start = None

    def test_joined(self):
        """Test join hook."""
        self.ep.joined()
        self.set_flag.assert_called_once_with(
            "{}.connected".format(self.ep_name)
        )

    def test_broken_or_departed(self):
        """Test broken/departed hook."""
        self.ep.broken_or_departed()
        self.clear_flag.assert_called_once_with(
            "{}.connected".format(self.ep_name)
        )

    def test_is_access_provided(self):
        """Test successful access."""
        self.fake_unit.received_raw = {
            "host": TEST_IP,
            "port": TEST_PORT,
            "username": "user",
            "password": "password"
        }

        self.assertEqual(self.ep.host, TEST_IP)
        self.assertEqual(self.ep.port, TEST_PORT)
        self.assertEqual(self.ep.username, "user")
        self.assertEqual(self.ep.password, "password")
        self.assertTrue(self.ep.is_access_provided())

    def test_is_access_provided_failed(self):
        """Test failed to grant access."""
        self.fake_unit.received_raw = {
            "username": "user",
            "password": "password"
        }

        self.assertEqual(self.ep.port, 3306)
        self.assertEqual(self.ep.username, "user")
        self.assertEqual(self.ep.password, "password")
        self.assertFalse(self.ep.is_access_provided())

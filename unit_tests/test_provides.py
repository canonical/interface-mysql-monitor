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

import provides

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
            },
            "not_unless": {
                "provide_access": ("{endpoint_name}.connected", )
            }
        }
        # test that the hooks were registered
        self.registered_hooks_test_helper(provides, hook_set, defaults)


class TestMySQLMonitorProvides(test_utils.PatchHelper):

    def setUp(self):
        """Set up before each test."""
        super().setUp()
        self._patches = {}
        self._patches_start = {}
        self.patch_object(provides, "clear_flag")
        self.patch_object(provides, "set_flag")
        self.patch_object(provides.ch_net_ip, "get_relation_ip", return_value=TEST_IP)

        self.fake_unit = mock.MagicMock()
        self.fake_unit.unit_name = "mysql-innodb-cluster/4"

        self.fake_relation_id = "db-monitor:42"
        self.fake_relation = mock.MagicMock()
        self.fake_relation.relation_id = self.fake_relation_id
        self.fake_relation.units = [self.fake_unit]

        self.ep_name = "db-monitor"
        self.ep = provides.MySQLMonitor(
            self.ep_name, [self.fake_relation_id])
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

    def test_departed_or_broken(self):
        """Test departed/broken hook."""
        self.ep.broken_or_departed()
        self.clear_flag.assert_called_once_with(
            "{}.connected".format(self.ep_name)
        )
        self.fake_relation.to_publish.update.assert_called_once_with({
            "host": None,
            "port": None,
            "username": None,
            "password": None,
        })

    def test_provide_access(self):
        """Test the provide of MySQL credentials in relation to the data."""
        self.ep.provide_access(TEST_PORT, "user", "password")
        self.fake_relation.to_publish.update.assert_called_once_with({
            "host": TEST_IP,
            "port": TEST_PORT,
            "username": "user",
            "password": "password",
        })

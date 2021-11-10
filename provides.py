#!/usr/bin/python
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import charmhelpers.contrib.network.ip as ch_net_ip

from charms.reactive import Endpoint
from charms.reactive import set_flag, clear_flag
from charms.reactive import not_unless, when, when_any


class MySQLMonitor(Endpoint):
    @property
    def relation_ip(self):
        """Get IP of related endpoint.

        :return: IP address of related endpoint
        :rtype: Optional[str]
        """
        return ch_net_ip.get_relation_ip(self.endpoint_name)

    @when("endpoint.{endpoint_name}.joined")
    def joined(self):
        """Handle joined relation."""
        set_flag(self.expand_name("{endpoint_name}.connected"))

    @when_any("endpoint.{endpoint_name}.broken",
              "endpoint.{endpoint_name}.departed")
    def broken_or_departed(self):
        """Handle broken relation."""
        for relation in self.relations:
            relation.to_publish_raw["host"] = None
            relation.to_publish_raw["port"] = None
            relation.to_publish_raw["username"] = None
            relation.to_publish_raw["password"] = None

        clear_flag(self.expand_name("{endpoint_name}.connected"))

    @not_unless("{endpoint_name}.connected")
    def provide_access(self, port, user, password):
        """Provide a access credentials to established connection.

        :param port: port to established connection with MySQL
        :type: int
        :param user: user to established connection with MySQL
        :type: str
        :param password: password to established connection with MySQL
        :type: str
        """
        for relation in self.relations:
            relation.to_publish_raw["host"] = self.relation_ip
            relation.to_publish_raw["port"] = port
            relation.to_publish_raw["username"] = user
            relation.to_publish_raw["password"] = password

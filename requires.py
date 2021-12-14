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

from charms.reactive import Endpoint
from charms.reactive import when, when_any
from charms.reactive import set_flag, clear_flag


class MySQLMonitorClient(Endpoint):
    @when("endpoint.{endpoint_name}.joined")
    def joined(self):
        set_flag(self.expand_name("{endpoint_name}.connected"))

    @when_any(
        "endpoint.{endpoint_name}.departed",
        "endpoint.{endpoint_name}.broken"
    )
    def broken_or_departed(self):
        clear_flag(self.expand_name("{endpoint_name}.connected"))

    @property
    def host(self):
        """Return the host for the provided database."""
        return self.all_joined_units.received["host"]

    @property
    def port(self):
        """Return the port the provided database.
        If not available, returns the default port of 3306.
        """
        return self.all_joined_units.received.get("port", 3306)

    @property
    def username(self):
        """Return the username for the provided database."""
        return self.all_joined_units.received["username"]

    @property
    def password(self):
        """Return the password for the provided database."""
        return self.all_joined_units.received["password"]

    def is_access_provided(self):
        """Check if all credentials are available."""
        return all([self.host, self.port, self.username, self.password])

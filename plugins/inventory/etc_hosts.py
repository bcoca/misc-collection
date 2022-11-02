# Copyright (c) 2022 Brian Coca
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    name: bcoca.misc.etc_hosts
    short_description: Use /etc/host as an inventory source
    description:
        - Generate an inventory based on /etc/hosts entries
    extends_documentation_fragment:
      - constructed
    options:
        hosts_file:
            description: Location of the host file .. should really be /etc/hosts ...
            type: path
            default: '/etc/hosts'
        skip_localhost:
            description: If C(True), it will avoid creating C(localhost) entries and rely on the "implicit localhost" instead.
            type: bool
            default: true
        prefix:
            description: prefix for intenral variables
            default: etc_hosts_
        inventory_name:
            description: Choose which method to use to determine inventory_hostname.
            default: 'use_ip'
            choices:
                use_ip: The first column (the IP) will be used, no ansilbe_host is set.
                first: First alias after the IP.
                shortest: First shortest alias found.
                fqdn: First fully qualified domain name found (entry with dots in name).
                all: Each alias creates a new entry.
                every_nonfqdn: Only names without dots create a new host.
                every_fqdn: Only FQDN entries (with dots) create a new host.
'''

EXAMPLES = ''' # wyho
 '''
'''
        notes:
            - The ''every_'' options for C(inventory_name) will create multiple hosts but, every other option sets ansible_host to the IP.
            - All C(inventory_name) choices set C(ansible_host) to the IP except C(use_ip), which does not set the variable.
'''

from ansible import constants as C
from ansible.errors import AnsibleParserError, AnsibleOptionsError
from ansible.module_utils._text import to_bytes, to_text
from ansible.plugins.inventory import BaseInventoryPlugin, Constructable


class InventoryModule(BaseInventoryPlugin, Constructable):
    """
    Reads a YAML config file and reads /etc/hosts on the local system
    to build a host inventory.
    """
    NAME = 'bcoca.misc.etc_hosts'
    _COMMENT = u'#'
    b_COMMENT = to_bytes(_COMMENT)

    def verify_file(self, path):
        valid = False
        if super(InventoryModule, self).verify_file(path):
            if path.endswith(('etc_hosts.yaml', 'etc_hosts.yml')):
                valid = True
        return valid

    def _add_host_and_vars(self, hostname, variables):

        if hostname in self.inventory.hosts:
            # aggregate inventory_a/c
            variables[self._aliases] = self.inventory.get_host(hostname).get_vars().get(self._aliases, []) + variables[self._aliases]
            variables[self._comments] = self.inventory.get_host(hostname).get_vars().get(self._comments, []) + variables[self._comments]
        else:
            self.inventory.add_host(hostname)

        for varname in variables:
            self.inventory.set_variable(hostname, varname, variables[varname])

    def _do_compose(self, hosts):

        strict = self.get_option('strict')
        compose = self.get_option('compose')
        groups = self.get_option('groups')
        keyed = self.get_option('keyed_groups')

        for host in hosts:
            hostvars = self.inventory.get_host(host).get_vars()
            if compose:
                self._set_composite_vars(compose, hostvars[host], host, strict=strict)

            if groups:
                # constructed groups based on conditionals
                self._add_host_to_composed_groups(groups, hostvars[host], host, strict=strict)

            if keyed:
                # constructed keyed_groups
                self._add_host_to_keyed_groups(keyed, hostvars[host], host, strict=strict)

    def process(self, hosts):

        skip_local = self.get_option('skip_localhost')
        iname = self.get_option('inventory_name')

        done = []
        for host in hosts:
            variables = {self._aliases: hosts[host]['aliases'], self._comments: hosts[host]['comments']}
            if host in C.LOCALHOST:
                if skip_local:
                    continue
                variables['ansible_connection'] = 'local'
                variables['ansible_python_interpreter'] = '{{ansible_playbook_python}}'

            # now choose name, default to IP
            variables['ansible_host'] = host
            if iname == 'use_ip':
                del variables['ansible_host']
                self._add_host_and_vars(host, variables)
            elif iname in ('all', 'every_fqdn', 'every_nonfqdn'):
                raise AnsibleParserError('%s IS NOT IMPLEMENTED YET, choose another!!!!' % iname)
                for name in variables[self._aliases]:
                    if iname != 'all':
                        hasdot = bool('.' in name)
                        if (iname == 'every_fqdn' and not hasdot) or (iname == 'every_nonfqdn' and hasdot):
                            continue
                    self._add_host_and_vars(name, variables)
                    done.append(name)
            else:
                if iname == 'first':
                    name = variables[self._aliases][0]
                #elif iname == 'fqdn'
                #    name = ?
                #    del variables[self._aliases][name]
                #elif iname == 'shortest'
                #    name = ?
                else:
                    raise AnsibleParserError('%s IS NOT IMPLEMENTED YET, choose another!!!!' % iname)

                # remove name from aliases
                variables[self._aliases].remove(name)
                self._add_host_and_vars(name, variables)
                done.append(name)

        return done

    def parse(self, inventory, loader, path, cache=True):

        super(InventoryModule, self).parse(inventory, loader, path)

        # set _options from config data
        config_data = self._read_config_data(path)
        self._consume_options(config_data)

        # for use later
        prefix = self.get_option('prefix')
        self._aliases = '%saliases' % prefix
        self._comments = '%scomments' % prefix

        # get the actual data
        hosts_path = self.get_option('hosts_file')
        try:
            # Read in /etc/hosts
            with open(to_bytes(hosts_path), 'rb') as fh:
                b_data = fh.read()
        except (IOError, OSError) as e:
            raise AnsibleOptionsError(e)

        # ensure we can read it
        data = []
        try:
            data = to_text(b_data, errors='surrogate_or_strict').splitlines()
        except UnicodeError:
            # deal with non encodable line by line, skip comments
            data = []
            for line in b_data.splitlines():
                line = line.strip()

                # skip comments/empty
                if not line or line.startswith(self.b_COMMENT):
                    continue

                try:
                    data.append(to_text(line, errors='surrogate_or_strict'))
                except UnicodeError as e:
                    # it was data line after all, still an error
                    raise AnsibleParserError(e)

        # parse text into data structure to process
        hosts = {}
        for line in data:
            line = line.strip()

            # skip pure comment lines
            if not line or line.startswith(self._COMMENT):
                continue

            # save inline comments and assign to the host
            comment = None
            if self._COMMENT in line:
                line, comment = line.split(self._COMMENT, 1)
                comment = comment.strip()

            # process rest of line as ip + aliases
            first = None
            for entry in line.split():

                if first is not None:
                    if entry not in hosts[first]['aliases']:
                        hosts[first]['aliases'].append(entry)
                elif entry not in hosts:
                    hosts[entry] = {'aliases': [], 'comments': []}

                if first is None:
                    first = entry

            if comment is not None and comment not in hosts[first]['comments']:
                # add comment to host if not dupe
                hosts[first]['comments'].append(comment)

        self._do_compose(self.process(hosts))

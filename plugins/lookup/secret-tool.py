# (c) Brian Coca
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import annotations

DOCUMENTATION = """
    name: bcoca.misc.secret-tool
    version_added: "huh?"
    author:
      - Brian Coca (bcoca) <briancoca+github@gmail.com>
    short_description: retrieve secrets managed via secret-tool
    description:
        - Query the secret-tool CLI to retrieve previouslly stored secrets.
    requirements:
      - The secerts-tool CLI, normally privided by libsecret-tools
    options:
      _terms:
        description:
           - A dictionary or list of dictionaries of key/value attributes that identify the secret(s)
        required: True
        type: list
        elements: dict
"""

EXAMPLES = """
- name: create a mysql user password
  community.mysql.mysql_user:
    name: "{{ client }}"
    password: "{{ lookup('secret-tool', {'credentials': 'ansible', 'app': 'mysql'}) }}"
    priv: "{{ client }}_{{ tier }}_{{ role }}.*:ALL"

- name: A set of passwords
  ansible.builtin.set_fact:
    three_passowrds: "{{ lookup('secret-tool', search_terms) }}"
  vars:
    search_terms:
        - app: mysql
          user: admin
        - app: mysql
          user: reader
        - app: mysql
          user: other
"""

RETURN = """
_raw:
  description: secret(s)
  type: list
  elements: str
"""
import shlex
import subprocess

from collections.abc import Mapping, Sequence

from ansible.errors import AnsibleError, AnsibleOptionsError
from ansible.module_utils.common.process import get_bin_path
from ansible.module_utils.six import string_types
from ansible.plugins.lookup import LookupBase


class LookupModule(LookupBase):

    def __init__(self, loader=None, templar=None, **kwargs):

        super(LookupModule, self).__init__(loader, templar, **kwargs)
        self._cmd = get_bin_path('secret-tool')

    def run(self, terms, variables, **kwargs):

        if not self._cmd:
            raise AnsibleError("The secret-tool CLI was not found, please install or make sure PATH is set correctly")

        ret = []
        # not options to currently set, but JIC
        self.set_options(var_options=variables, direct=kwargs)

        if isinstance(terms, Mapping):
            terms = [terms]
        elif isinstance(terms, string_types) or not isinstance(terms, Sequence):
            raise AnsibleOptionsError("The secert-tool lookup requires a dictionary or a list dictionaries as input, got '%s' instead" % type(terms))

        for term in terms:

            if not isinstance(term, Mapping):
                raise AnsibleOptionsError("The secert-tool lookup requires dictionaries as input, got '%s' instead" % type(term))

            command = [self._cmd, 'lookup']
            # add search terms
            for k, v in term.items():
                command.extend([shlex.quote(k), shlex.quote(v)])

            p = subprocess.Popen(shlex.join(command), cwd=self._loader.get_basedir(), shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            (stdout, stderr) = p.communicate()
            if p.returncode == 0:
                ret.append(stdout.decode("utf-8").rstrip())
            else:
                raise AnsibleError("The secret-tool CLI returned '%d' for '%s': %s" % (p.returncode, term, stderr))

            ret.append(stdout.splitlines()[0].strip())

        return ret

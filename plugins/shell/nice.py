# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import annotations

DOCUMENTATION = '''
name: nice
short_description: "nice POSIX shell (/bin/sh)"
version_added: histerical
description:
  - This shell plugin is a copy the one you want to use on most Unix systems, but 'nicer', it is the most compatible and widely installed shell.
options:
    niceness:
        description: the value of 'nice' to be passed to executing a module
        default: 0
        type: int
extends_documentation_fragment:
  - shell_common
'''
import shlex

from ansible.plugins.shell.sh import ShellModule as Sh


class ShellModule(Sh):

    def build_module_command(self, env_string, shebang, cmd, arg_path=None):

        nice = self.get_option('niceness')
        if nice:
            cmd = f'nice -n {nice} {shlex.quote(cmd)}'
        return super().build_module_command(env_string, shebang, cmd, arg_path)

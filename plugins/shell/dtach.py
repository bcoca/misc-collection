# Copyright (c) 2025 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import annotations

DOCUMENTATION = """
name: dtach
short_description: dtach as command shell
version_added: historical
description:
  - This shell plugin is the one you want to use when debugging issues, it will still execute commands using the default shell but allow for you to attach to running commands. To use just set `ansbile_shell_type: bcoca.misc.dtach` for that task.
  - but cannot work  ...
extends_documentation_fragment:
  - shell_common
"""

import os
import shlex

from ansible.plugins.shell.sh import ShellModule as Sh

from ansible.utils.display import Display
display = Display()

class ShellModule(Sh):

    def build_module_command(self, env_string, shebang, cmd, arg_path=None):
        cmd = super(ShellModule, self).build_module_command(env_string, shebang, cmd, arg_path)

        sess = f'/tmp/.ansible_{os.getpid()}'
        display.warning(f"To attach to the running module process use: dtach -a {sess}")
        return f"dtach -c {sess} {cmd}"

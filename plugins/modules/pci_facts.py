# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import annotations


DOCUMENTATION = """
---
module: pci_facts
version_added: histerical
short_description: Gathers PCI facts about remote hosts
options:
    use_dns:
        description:
            - Use DNS to get descriptions not available locally.
            - This creates a local cache for lspci to reuse.
        type: bool
        default: false
        aliases: dns
    gather_timeout:
        description:
            - Set the timeout in seconds for fact gathering.
        type: int
        aliases: timeout
description:
    - This module just dumps facts as produced by lscpi command
extends_documentation_fragment:
  -  action_common_attributes
  -  action_common_attributes.facts
attributes:
    check_mode:
        support: full
    diff_mode:
        support: none
    facts:
        support: full
    platform:
        platforms: posix
author:
    - Brian Coca
"""

EXAMPLES = r"""
# Display pci facts from all hosts and store them indexed by `hostname` at `/tmp/facts`.
# ansible all -m pci_facts --tree /tmp/facts
"""
import signal

from ansible.module_utils.basic import AnsibleModule


def main():

    def _timeout(signum, frame):
        module.fail_json(f'Timeout of {timeout!r} exceeded while running lscpi.')

    module = AnsibleModule(
        argument_spec=dict(
            gather_timeout=dict(default=10, required=False, type='int', aliases=['timeout']),
            use_dns=dict(default=False, required=False, type='bool', aliases=['dns']),
        ),
        supports_check_mode=True,
    )

    timeout = module.params["gather_timeout"]
    try:
        lspci = module.get_bin_path('lspci')
    except ValueError as e:
        module.fail_json(f"{e!r}")

    # TODO: use -mm if all targets use newer lspci and switch to Slot for device id
    command = [lspci, '-vvvv', '-D', '-m', '-nn']

    if module.params['use_dns']:
        command.append('-q')

    signal.signal(signal.SIGALRM, _timeout)
    if timeout is not None:
        signal.alarm(timeout)

    try:
        rc, pcidata, err = module.run_command(command)
    finally:
        signal.alarm(0)

    if rc != 0:
        module.fail_json(f"Error when executing lspci: rc={rc!r} stderr={err!r}")

    devices = {}
    for record in pcidata.split("\n\n"):  # break on empty lines (each device)
        device = {}
        current = None
        for entry in record.split('\n'):
            if ':\t' not in entry:
                continue  # skip blanks
            k, v = entry.split(':\t', 1)
            if k == 'Device' and current is None:  # first 'Device' is always the pci id
                current = v  # domain:bus:device.func
                devices[v] = {}
            else:
                device[k] = v
        if device:
            devices[current] = device

    module.exit_json(result={'ansible_facts': {'pci': devices}})

if __name__ == '__main__':
    main()

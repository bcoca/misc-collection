# -*- coding: utf-8 -*-

# (c) 2012, Michael DeHaan <michael.dehaan@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import annotations


DOCUMENTATION = """
---
module: pci_facts
version_added: histerical
short_description: Gathers PCI facts about remote hosts
options:
    gather_timeout:
        version_added: "2.2"
        description:
            - Set the default timeout in seconds for individual fact gathering.
        type: int
        default: 10
description:
    - This module is automatically called by playbooks to gather useful
      variables about remote hosts that can be used in playbooks. It can also be
      executed directly by C(/usr/bin/ansible) to check what variables are
      available to a host. Ansible provides many I(facts) about the system,
      automatically.
    - This module is also supported for Windows targets.
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
    - "Ansible Core Team"
"""

EXAMPLES = r"""
# Display pci facts from all hosts and store them indexed by `hostname` at `/tmp/facts`.
# ansible all -m pci_facts --tree /tmp/facts
"""

from ansible.module_utils.basic import AnsibleModule

def main():
    module = AnsibleModule(
        argument_spec=dict(
            gather_timeout=dict(default=10, required=False, type='int'),
        ),
        supports_check_mode=True,
    )

    facts_dict = {}
    gather_timeout = module.params['gather_timeout']

    try:
        lspci = module.get_bin_path('lspci')
    except ValueError as e:
        module.fail_json(f"{e!r}")


    rc, pcidata, err = module.run_command([lspci, '-vvvv', '-D', '-m', '-nn'])
    if rc != 0:
        module.fail_json(f"Error when executing lspci: rc={rc!r} stderr={err!r}")

    devices = []
    for record in pcidata.split("\n\n"):
        device = {}
        for entry in record.split('\n'):
            if ':' not in entry:
                continue  # skip blanks
            k, v = entry.split(':\t')
            device[k] = v
        if device:
            devices.append(device)

    module.exit_json(result={'ansible_facts': {'pci': devices}})

if __name__ == '__main__':
    main()

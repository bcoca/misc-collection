# -*- coding: utf-8 -*-

# (c) 2023, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: facter_facts
version_added: histerical
short_description: Gathers facts about remote hosts using 'facter'
options:
    query:
        aliases: gather_subset
        description: Similar to gather subset it allows you to specify the specific a list facts you want to retrieve
        type: list
        elements: str
    fact_path:
        aliases: custom_dir
        description: Custom
        type: path
    load_puppet:
        description:
        type: bool
    load_ruby:
        description:
        type: bool
        default: true
    legacy:
        description:
        type: bool
description:
    - Gatheres facts provided by the 'facter' utility
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
requirements:
      The 'facter' utility must be installed remote systems and support JSON output.
    - The filter option filters only the first level subkey below ansible_facts.
author:
    - "Ansible Core Team"
'''

EXAMPLES = r"""
 - name: Restrict additional gathered facts to processors
   facter_facts:
     query: processors

 - name: Restrict additional gathered facts to processor type
   facter_facts:
     query: processors.isa

# Collect a few specific facts
#> ansible all -m facter_facts -a 'query=os.name,os.release.major,processors.isa'
"""

import json

from ansible.module_utils._text import to_text
from ansible.module_utils.basic import AnsibleModule


def find_facter(module):
    facter_path = module.get_bin_path('facter', opt_dirs=['/opt/puppetlabs/bin'])
    cfacter_path = module.get_bin_path('cfacter', opt_dirs=['/opt/puppetlabs/bin'])

    # Prefer to use cfacter if available
    if cfacter_path is not None:
        facter_path = cfacter_path

    return facter_path


def run_facter(module, facter_path, options):

    run = [facter_path, "--json", options]
    rc, out, err = module.run_command(run)
    return rc, out, err


def get_facter_output(module):

    facter_path = find_facter(module)
    if not facter_path:
        return None

    options = []
    if module.params['fact_path']:
        options.extend(["--custom-dir", module.params['fact_path']])

    if not module.params['load_ruby']:
        options.append("--no-ruby")

    if module.params['load_puppet']:
        options.append("--puppet")

    if module.params['legacy']:
        options.append("--show-legacy")

    if module.debug:
        options.append("-t")
        options.append("-d")

    if module.params['query']:
        options.append(' '.join(module.params['query']))

    rc, out, err = run_facter(module, facter_path, options)

    if rc != 0:
        return None

    return out


def collect(module, options):

    facter_dict = {}
    facter_output = get_facter_output(module)

    try:
        facter_dict = json.loads(facter_output)
    except json.JSONDecodeError as e:
        module.fail_json(msg=to_text(e))

    return facter_dict


def main():
    module = AnsibleModule(
        argument_spec=dict(
            query=dict(required=False, type='list', elements='str', default=''),
            fact_path=dict(aliases=['custom_dir'], default='/etc/ansible/facts.d', required=False, type='path'),
            load_ruby=dict(required=False, type='bool', default=True),
            load_puppet=dict(required=False, type='bool', default=False),
            legacy=dict(required=False, type='bool'),
        ),
        supports_check_mode=True,
    )

    facts = {'ansible_facts': {'facter': {}}}
    try:
        facts['ansible_facts']['facter'] = collect(module)
    except Exception as e:
        module.fail_json(msg=to_text(e))

    module.exit_json(facts)


if __name__ == '__main__':
    main()

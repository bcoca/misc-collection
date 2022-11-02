# (c) 2020 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


DOCUMENTATION = '''
    vars: site_host_group
    version_added: "1.0.0"
    short_description: Use static directory for group_vars and host_vars.
    requirements:
        - enable in configuration
    description:
        - Loads YAML vars into corresponding directory (see 'path' below) as part of the 'all' group.
        - Files are restricted by extension to one of .yaml, .json, .yml or no extension (see valid_extentions below).
        - Hidden (starting with '.') and backup (ending with '~') files and directories are ignored.
    options:
      path:
        description: directory that contains host_vars/ and group_vars/ directories under which Ansible will
                     match to group/hosts and load corresponding variable files.
        ini:
          - key: path
            section: vars_site_host_group
        env:
          - name: ANSIBLE_SITE_VARS_PATH
        type: path
        default: /etc/ansible/site/
      valid_extensions:
        default: [".yml", ".yaml", ".json"]
        description:
          - "Check all of these extensions when looking for 'variable' files which should be YAML or JSON or vaulted versions of these."
          - 'This affects vars_files, include_vars, inventory and vars plugins among others.'
        env:
          - name: ANSIBLE_YAML_FILENAME_EXT
        ini:
          - section: yaml_valid_extensions
            key: defaults
        type: list
'''
    #extends_documentation_fragment:
    #  - ansilbe.builtin.vars_plugin_staging

import os
from ansible.errors import AnsibleParserError
from ansible.module_utils._text import to_bytes, to_native, to_text
from ansible.plugins.vars import BaseVarsPlugin
from ansible.inventory.host import Host
from ansible.inventory.group import Group
from ansible.utils.vars import combine_vars

FOUND = {}


class VarsModule(BaseVarsPlugin):


    def get_vars(self, loader, path, entities, cache=True):
        ''' returns vars matching the configure path and entity type/names '''

        if not isinstance(entities, list):
            entities = [entities]

        # we ignore path given by vars manager, we use configured one instead
        path = self.get_option('path')

        super(VarsModule, self).get_vars(loader, path, entities)

        data = {}
        for entity in entities:
            if isinstance(entity, Host):
                subdir = 'host_vars'
            elif isinstance(entity, Group):
                subdir = 'group_vars'
            else:
                raise AnsibleParserError("Supplied entity must be Host or Group, got %s instead" % (type(entity)))

            # avoid 'chroot' type inventory hostnames /path/to/chroot
            if not entity.name.startswith(os.path.sep):
                try:
                    found_files = []
                    # load vars
                    b_opath = os.path.realpath(to_bytes(os.path.join(path, subdir)))
                    opath = to_text(b_opath)
                    key = '%s.%s' % (entity.name, opath)
                    if cache and key in FOUND:
                        found_files = FOUND[key]
                    else:
                        # no need to do much if path does not exist for basedir
                        if os.path.exists(b_opath):
                            if os.path.isdir(b_opath):
                                self._display.debug("\tprocessing dir %s" % opath)
                                found_files = loader.find_vars_files(opath, entity.name)
                                FOUND[key] = found_files
                            else:
                                self._display.warning("Found %s that is not a directory, skipping: %s" % (subdir, opath))

                    for found in found_files:
                        new_data = loader.load_from_file(found, cache=True, unsafe=True)
                        if new_data:  # ignore empty files
                            data = combine_vars(data, new_data)

                except Exception as e:
                    raise AnsibleParserError(to_native(e))
        return data

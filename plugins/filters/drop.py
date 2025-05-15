# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


from collections.abc import Sequence

def do_drop(obj, keys):

    if isinstance(obj, dict):
        for k in keys:
            del obj[k]
    elif isinstance(obj, Sequence):
        for k in keys:
            obj.remove(k)
    else:
        raise TypeError("Drop only works on dictionaries or lists")

    return obj

class FilterModule(object):
    ''' Ansible core jinja2 filters '''

    def filters(self):
        return {
            'drop': do_drop,
        }

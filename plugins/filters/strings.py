# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import difflib
import os

from collections.abc import Sequence

from ansible.errors import AnsibleError, AnsibleFilterError
from ansible.module_utils._text import to_bytes, to_text
from ansible.module_utils.six import string_types


def do_diff(a, b, fromfile='', tofile='', n=3, lineterm='\n'):

    def _get_diff_param(x, filename):

        filename = filename
        if os.path.exists(x):
            if not filename:
                filename = x
            try:
                with open(to_bytes(a), 'rb') as f:
                    b_content = f.read()
                    x = to_text(b_content, errors='surrogate_or_strict')
            except TypeError as e:
                raise AnsibleError('failed to convert text from "%s"' % (x), orig_exc=e)
            except (IOError, OSError) as e:
                raise AnsibleError('failed to open: %s' % x, orig_exc=e)

        if isinstance(x, string_types):
            x = x.split(lineterm)
        elif not isinstance(x, Sequence):
            raise TypeError('i want file, stirng or list of strings!!!')
        else:
            bad = [y for y in x if not isinstance(y, string_types)]
            if bad:
                raise TypeError('you gave me a list with stuff that is not a string!')

        return x, filename

    try:
        a, fromfile = _get_diff_param(a)
        b, tofile = _get_diff_param(b)
        return lineterm.join(difflib.unified_diff(a, b, fromfile, tofile, n=n, lineterm=lineterm))
    except Exception as e:
        raise AnsibleFilterError('bad diff', orig_exc=e)


class FilterModule(object):
    ''' Ansible core jinja2 filters '''

    def filters(self):
        return {
            'diff': do_diff,
        }

# (c) Brian Coca
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import annotations

DOCUMENTATION = """
    name: smartjson
    short_description: smart storage in JSON files.
    description:
        - This cache selectively stores in serialized JSON files, per host.
    author: me
    options:
      _uri:
        required: True
        description:
          - Path in which the cache plugin will save the JSON files
        env:
          - name: ANSIBLE_CACHE_PLUGIN_CONNECTION
          - name: ANSIBLE_SMARTJSON_CACHE_PLUGIN_CONNECTION
        ini:
          - key: fact_caching_connection
            section: defaults
          - key: connection
            section: smartjson_cache_plugin
        type: path
      _prefix:
        description: User defined prefix to use when creating the JSON files
        env:
          - name: ANSIBLE_CACHE_PLUGIN_PREFIX
          - name: ANSIBLE_SMARTJSON_CACHE_PLUGIN_PREFIX
        ini:
          - key: fact_caching_prefix
            section: defaults
          - key: prefix
            section: smartjson_cache_plugin
      _timeout:
        default: 86400
        description: Expiration timeout for the cache plugin data
        env:
          - name: ANSIBLE_CACHE_PLUGIN_TIMEOUT
          - name: ANSIBLE_SMARTJSON_CACHE_PLUGIN_TIMEOUT
        ini:
          - key: fact_caching_timeout
            section: defaults
          - key: timeout
            section: smartjson_cache_plugin
        type: integer
     filter:
        description: List of variable names to avoid caching
        type: list
        element: str
        env:
          - name: ANSIBLE_SMARTJSON_FILTER
        ini:
          - key: timeout
            section: smartjson_cache_plugin
"""

import json
import pathlib

from ansible.plugins.cache import BaseFileCacheModule


class CacheModule(BaseFileCacheModule):
    """A smart caching module backed by json files."""

    _persistent = False  # Avoid x2 JSON

    def set(self, key, value):
        rval = value
        if banned := self.get_option('filter') and isinstance(value, dict):
            rval = {k: value[k] for k in value.keys() if k not in banned}
        super().set(key, rval)

    def _load(self, jsonfile: str) -> object:
        with pathlib.Path(jsonfile) as jfile:
            return json.loads(jfile.read_text())

    def _dump(self, value: object, jsonfile: str) -> None:
        with pathlib.Path(jsonfile) as jfile:
            jfile.write_text(json.dumps(value))

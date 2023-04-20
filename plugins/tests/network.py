# (c) Ansible Project

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import ipaddress
import re

main = r"^([0-9a-f]{2}[:-]){5}[0-9a-f]{2}$"
cisco = r"^([0-9a-f]{4}\.[0-9a-f]{4}\.[0-9a-f]{4})$"
bare = r"^[0-9a-f]{12}$"
mac = re.compile(f"(?i){main}|{cisco}|{bare}")


def valid_mac_address(mac):
    return bool(mac.match(mac))


def valid_ip_address(ip):

    valid = False
    try:
        dummy = ipaddress.ip_address(ip)
        valid = True
    except ValueError:
        pass
    return valid


def valid_ipv4_address(ip):

    valid = False
    try:
        dummy = ipaddress.IPv4Address(ip)
        valid = True
    except ValueError:
        pass

    return valid


def valid_ipv6_address(ip):

    valid = False
    try:
        dummy = ipaddress.IPv6Address(ip)
        valid = True
    except ValueError:
        pass

    return valid


def valid_ip_mask(mask):

    valid = False
    try:
        dummy = ipaddress.ip_network(f'127.0.0.1/{mask}')
        valid = True
    except ValueError:
        pass

    return valid


def valid_ipv4_mask(mask):

    valid = False
    try:
        dummy = ipaddress.IPv4Network(f'127.0.0.1/{mask}')
        valid = True
    except ValueError:
        pass

    return valid


def valid_ipv6_mask(mask):

    valid = False
    try:
        dummy = ipaddress.IPv6Network(f'::1/{mask}')
        valid = True
    except ValueError:
        pass

    return valid


def is_multicast(ip):

    try:
        is_ip = ipaddress.ip_address(ip)
    except ValueError:
        return False

    return is_ip.is_multicast


def is_private(ip):

    try:
        is_ip = ipaddress.ip_address(ip)
    except ValueError:
        return False

    return is_ip.is_private


def is_global(ip):

    try:
        is_ip = ipaddress.ip_address(ip)
    except ValueError:
        return False

    return is_ip.is_global


def is_unspecified(ip):

    try:
        is_ip = ipaddress.ip_address(ip)
    except ValueError:
        return False

    return is_ip.is_unspecified


def is_reserved(ip):

    try:
        is_ip = ipaddress.ip_address(ip)
    except ValueError:
        return False

    return is_ip.is_reserved


def is_loopback(ip):

    try:
        is_ip = ipaddress.ip_address(ip)
    except ValueError:
        return False

    return is_ip.is_loopback


def is_link_local(ip):

    try:
        is_ip = ipaddress.ip_address(ip)
    except ValueError:
        return False

    return is_ip.is_link_local


class TestModule(object):

    def tests(self):
        return {
            # file testing
            'mac_address': valid_mac_address,
            'mac_addr': valid_mac_address,

            'ipv4_mask': valid_ipv4_mask,
            'ipv4_address': valid_ipv4_address,
            'ipv4_addr': valid_ipv4_address,

            'ipv6_mask': valid_ipv6_mask,
            'ipv6_address': valid_ipv6_address,
            'ipv6_addr': valid_ipv6_address,

            'ip_mask': valid_ip_mask,
            'ip_address': valid_ip_address,
            'ip_addr': valid_ip_address,

            'multicast_ip': is_multicast,
            'private_ip': is_private,
            'global_ip': is_global,
            'unspecified_ip': is_unspecified,
            'reserved_ip': is_reserved,
            'loopback_ip': is_loopback,
            'link_local_ip': is_link_local,
        }

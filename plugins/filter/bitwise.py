# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


def do_band(a: int, b: int):
    return a & b


def do_bor(a: int, b: int):
    return a | b


def do_bxor(a: int, b: int):
    return a ^ b


def do_bnot(a: int):
    return ~ a


def do_bleft(a: int, b: int):
    return a << b


def do_bright(a: int, b: int):
    return a >> b


class FilterModule(object):
    ''' Bitwise operations '''

    def filters(self):
        return {
            'bAND': do_band,
            'bOR': do_bor,
            'bXOR': do_bxor,
            'bNOT': do_bnot,
            'bLEFT': do_bleft,
            'bRIGHT': do_bright,
        }

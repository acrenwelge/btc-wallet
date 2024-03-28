#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Modified from source: https://github.com/0x9090/CrypocurrencyAddressValidation/blob/1e351c4e71248bd6fbcfb42af7003075f6a9c64a/Validation.py

# ====================================
# Cryptocurrency Validation Functions
# BTC
#
# Code modified from:
#
# Base58 decoding: https://github.com/keis/base58
# P2PKH validation: http://bit.ly/2DSVAXc
# Bech32 Validation: http://bit.ly/2Eaw40N

# Validation Levels
# 1. Length - Ensure the given address is the expected length
# 2. Character Set - Ensure that only the expected characters are used in the address
# 3. Character Position - Ensure that certain key characters are in their expected positions in the address
# 4. Cryptographic - Deconstruct the address into its logical components, and validate that it parsed, and any checksums or signatures are correct

# This library performs Levels 1 through 4 for all supported coins and address formats

# Supported Address Formats:
# | Type | Encoding | Supported? |
# |------|----------| ----------- |
# | P2PK | Hex      | No   |
# | P2PKH| Base58   | Yes  |
# | P2SH | Base58   | Yes  |
# | P2WPKH (Segwit) | Bech32  | Yes  |
# | P2WSH (Segwit)| Bech32  | Yes  |
# ====================================

import os
import sys

if os.path.exists(os.getcwd() + "\\venv"):
    sys.path.append(os.getcwd() + "\\venv\\Lib\\site-packages")
import operator as _oper
import re
from binascii import hexlify, unhexlify
from decimal import Decimal

import base58
import sha3

# --------------------- Global Variables -------------------- #

_ADDR_REGEX = re.compile(
    r"^[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{95}$"
)
_str_types = (str, bytes)
indexbytes = _oper.getitem
intlist2bytes = bytes
int2byte = _oper.methodcaller("to_bytes", 1, "big")
b = 256
q = 2**255 - 19
l = 2**252 + 27742317777372353535851937790883648493
PICONERO = Decimal("0.000000000001")
EMPTY_KEY = "0" * 64


# ----------------- Global Functions ----------------- @
def expmod(b, e, m):
    if e == 0:
        return 1
    t = expmod(b, e // 2, m) ** 2 % m
    if e & 1:
        t = (t * b) % m
    return t


def inv(x):
    return expmod(x, q - 2, q)


d = -121665 * inv(121666)
I = expmod(2, (q - 1) // 4, q)


def xrecover(y):
    xx = (y * y - 1) * inv(d * y * y + 1)
    x = expmod(xx, (q + 3) // 8, q)
    if (x * x - xx) % q != 0:
        x = (x * I) % q
    if x % 2 != 0:
        x = q - x
    return x


def compress(P):
    zinv = inv(P[2])
    return (P[0] * zinv % q, P[1] * zinv % q)


def decompress(P):
    return (P[0], P[1], 1, P[0] * P[1] % q)


By = 4 * inv(5)
Bx = xrecover(By)
B = [Bx % q, By % q]


def edwards(P, Q):
    x1 = P[0]
    y1 = P[1]
    x2 = Q[0]
    y2 = Q[1]
    x3 = (x1 * y2 + x2 * y1) * inv(1 + d * x1 * x2 * y1 * y2)
    y3 = (y1 * y2 + x1 * x2) * inv(1 - d * x1 * x2 * y1 * y2)
    return [x3 % q, y3 % q]


def add(P, Q):
    A = (P[1] - P[0]) * (Q[1] - Q[0]) % q
    B = (P[1] + P[0]) * (Q[1] + Q[0]) % q
    C = 2 * P[3] * Q[3] * d % q
    D = 2 * P[2] * Q[2] % q
    E = B - A
    F = D - C
    G = D + C
    H = B + A
    return (E * F, G * H, F * G, E * H)


def add_compressed(P, Q):
    return compress(add(decompress(P), decompress(Q)))


def scalarmult(P, e):
    if e == 0:
        return [0, 1]
    Q = scalarmult(P, e // 2)
    Q = edwards(Q, Q)
    if e & 1:
        Q = edwards(Q, P)
    return Q


def encodeint(y):
    bits = [(y >> i) & 1 for i in range(b)]
    return b"".join(
        [int2byte(sum([bits[i * 8 + j] << j for j in range(8)])) for i in range(b // 8)]
    )


def encodepoint(P):
    x = P[0]
    y = P[1]
    bits = [(y >> i) & 1 for i in range(b - 1)] + [x & 1]
    return b"".join(
        [int2byte(sum([bits[i * 8 + j] << j for j in range(8)])) for i in range(b // 8)]
    )


def bit(h, i):
    return (indexbytes(h, i // 8) >> (i % 8)) & 1


def isoncurve(P):
    x = P[0]
    y = P[1]
    return (-x * x + y * y - 1 - d * x * x * y * y) % q == 0


def decodeint(s):
    return sum(2**i * bit(s, i) for i in range(0, b))


def decodepoint(s):
    y = sum(2**i * bit(s, i) for i in range(0, b - 1))
    x = xrecover(y)
    if x & 1 != bit(s, b - 1):
        x = q - x
    P = [x, y]
    if not isoncurve(P):
        raise Exception("decoding point that is not on curve")
    return P


def public_from_secret(k):
    keyInt = decodeint(k)
    aB = scalarmult(B, keyInt)
    return encodepoint(aB)


def public_from_secret_hex(hk):
    return hexlify(public_from_secret(unhexlify(hk))).decode()


def bech32_decode(bech):
    charset = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"
    if (any(ord(x) < 33 or ord(x) > 126 for x in bech)) or (
        bech.lower() != bech and bech.upper() != bech
    ):
        return False
    bech = bech.lower()
    pos = bech.rfind("1")
    if pos < 1 or pos + 7 > len(bech) or len(bech) > 90:
        return False
    if not all(x in charset for x in bech[pos + 1 :]):
        return False
    hrp = bech[:pos]
    data = [charset.find(x) for x in bech[pos + 1 :]]
    if not bech32_verify_checksum(hrp, data):
        return False
    return True


def bech32_polymod(values):
    generator = [0x3B6A57B2, 0x26508E6D, 0x1EA119FA, 0x3D4233DD, 0x2A1462B3]
    chk = 1
    for value in values:
        top = chk >> 25
        chk = (chk & 0x1FFFFFF) << 5 ^ value
        for i in range(5):
            chk ^= generator[i] if ((top >> i) & 1) else 0
    return chk


def bech32_hrp_expand(hrp):
    return [ord(x) >> 5 for x in hrp] + [0] + [ord(x) & 31 for x in hrp]


def bech32_verify_checksum(hrp, data):
    return bech32_polymod(bech32_hrp_expand(hrp) + data) == 1


def hextobin(hexstr):
    if (hexstr.length % 2) is not 0:
        return False
    res = list()
    index = 0
    for char in hexstr:
        res[index] = int(hexstr[(index * 2) : (index * 2 + 2)])
        index += 1
    return res


class BaseAddress(object):
    label = None

    def __init__(self, addr, label=None):
        addr = str(addr)
        if not _ADDR_REGEX.match(addr):
            raise ValueError(
                "Address must be 95 characters long base58-encoded string, "
                "is {addr} ({len} chars length)".format(addr=addr, len=len(addr))
            )
        self._decode(addr)
        self.label = label or self.label

    def is_mainnet(self):
        """Returns `True` if the address belongs to mainnet.
        :rtype: bool
        """
        return self._decoded[0] == self._valid_netbytes[0]

    def is_testnet(self):
        """Returns `True` if the address belongs to testnet.
        :rtype: bool
        """
        return self._decoded[0] == self._valid_netbytes[1]

    def is_stagenet(self):
        """Returns `True` if the address belongs to stagenet.
        :rtype: bool
        """
        return self._decoded[0] == self._valid_netbytes[2]

    def _decode(self, address):
        self._decoded = bytearray(unhexlify(xmr_base58_decode(address)))
        checksum = self._decoded[-4:]
        if checksum != sha3.keccak_256(self._decoded[:-4]).digest()[:4]:
            raise ValueError("Invalid checksum in address {}".format(address))
        if self._decoded[0] not in self._valid_netbytes:
            raise ValueError(
                "Invalid address netbyte {nb}. Allowed values are: {allowed}".format(
                    nb=self._decoded[0],
                    allowed=", ".join(map(lambda b: "%02x" % b, self._valid_netbytes)),
                )
            )

    def __repr__(self):
        return xmr_base58_encode(hexlify(self._decoded))

    def __eq__(self, other):
        if isinstance(other, BaseAddress):
            return str(self) == str(other)
        if isinstance(other, _str_types):
            return str(self) == other
        return super(BaseAddress, self).__eq__(other)

    def __hash__(self):
        return hash(str(self))


# ------------------ Validation Class ----------------- #


class Validation:
    @staticmethod
    def is_btc_chain(chain):
        chain = chain.lower()
        chains = ["main", "testnet"]
        if chain in chains:
            return True
        return False

    @classmethod
    def is_btc_address(cls, address):  # Level 4 Validation
        match cls.get_btc_addr_type(address):
            case "P2PKH":
                return base58.b58decode_check(address)
            case "P2SH":
                return base58.b58decode_check(address)
            case "P2WPKH":
                return bech32_decode(address)
            case "BIP32 pubkey":
                return True
            case "testnet P2PKH":
                return base58.b58decode_check(address)
            case "testnet P2SH":
                return base58.b58decode_check(address)
            case "testnet P2WPKH":
                return bech32_decode(address)
            case "testnet BIP32 pubkey":
                return True
            case _:
                return False
        # if address[0] == "1":  # P2PKH Address
        #     return base58.b58decode_check(address)
        # elif address[0] == "3":  # P2SH Address
        #     return base58.b58decode_check(address)
        # elif address.startswith("bc1"):  # Bech32 Addresses (Segwit)
        #     return bech32_decode(address)
        # else:
        #     return False

    @staticmethod
    def get_btc_addr_type(address):
        if address[0] == "1":
            return "P2PKH"
        elif address[0] == "3":
            return "P2SH"
        elif address.startswith("bc1"):  # Bech32 Addresses (Segwit)
            return "P2WPKH"
        elif address.startswith("xpub"):
            return "BIP32 pubkey"
        elif address[0] == "m" or address[0] == "n":
            return "testnet P2PKH"
        elif address[0] == "2":
            return "testnet P2SH"
        elif address.startswith("tb1"):
            return "testnet P2WPKH"
        elif address.startswith("tpub"):
            return "testnet BIP32 pubkey"
        else:
            return None

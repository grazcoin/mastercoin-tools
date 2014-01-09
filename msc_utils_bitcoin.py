#!/usr/bin/python
import json
import hashlib
import re
from ecdsa import curves, ecdsa
# taken from https://github.com/warner/python-ecdsa
from pycoin import encoding
# taken from https://github.com/richardkiss/pycoin
from msc_utils_general import *

blocks_consider_new=3
blocks_consider_mature=6
max_currency_value=21000000

__b58chars = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
__b58base = len(__b58chars)

def to_satoshi(value):
    return int(float(value)*100000000+0.5)

def from_satoshi(value):
    float_number=int(value)/100000000.0
    return formatted_decimal(float_number)

def from_hex_satoshi(value):
    float_number=int(value,16)/100000000.0
    return formatted_decimal(float_number)

def b58encode(v):
  """ encode v, which is a string of bytes, to base58.
"""

  long_value = 0L
  for (i, c) in enumerate(v[::-1]):
    long_value += (256**i) * ord(c)

  result = ''
  while long_value >= __b58base:
    div, mod = divmod(long_value, __b58base)
    result = __b58chars[mod] + result
    long_value = div
  result = __b58chars[long_value] + result

  # Bitcoin does a little leading-zero-compression:
  # leading 0-bytes in the input become leading-1s
  nPad = 0
  for c in v:
    if c == '\0': nPad += 1
    else: break

  return (__b58chars[0]*nPad) + result


def b58decode(v, length):
    """ decode v into a string of len bytes
    """
    long_value = 0L
    for (i, c) in enumerate(v[::-1]):
      long_value += __b58chars.find(c) * (__b58base**i)

    result = ''
    while long_value >= 256:
      div, mod = divmod(long_value, 256)
      result = chr(mod) + result
      long_value = div
    result = chr(long_value) + result

    nPad = 0
    for c in v:
      if c == __b58chars[0]: nPad += 1
      else: break

    result = chr(0)*nPad + result
    if length is not None and len(result) != length:
      return None

    return result


def hash_160_to_bc_address(h160):
    vh160 = "\x00"+h160  # \x00 is version 0
    h3=hashlib.sha256(hashlib.sha256(vh160).digest()).digest()
    addr=vh160+h3[0:4]
    return b58encode(addr)

def bc_address_to_hash_160(addr):
    vh160_with_checksum=b58decode(addr, 25)
    return vh160_with_checksum[1:-4]

def get_sha256(string):
    return hashlib.sha256(string).hexdigest()

def is_script_output(output):
    # check that the script looks like:
    # 1 [ hex ] ...
    return output.startswith('1 [ ')

def is_script_multisig(output):
    # check that the script looks like:
    # 1 [ pubkey1 ] .. [ hex ] [ 2 of 3 ] checkmultisig
    return is_script_output(output) and output.endswith('checkmultisig')

def is_pubkey_valid(pubkey):
    try:
        sec=encoding.binascii.unhexlify(pubkey)
        public_pair=encoding.sec_to_public_pair(sec)
        return curves.ecdsa.point_is_valid(ecdsa.generator_secp256k1, public_pair[0], public_pair[1])
    except TypeError:
        return False

def get_compressed_pubkey_format(pubkey):
    public_pair=encoding.sec_to_public_pair(encoding.binascii.unhexlify(pubkey))
    return encoding.binascii.hexlify(encoding.public_pair_to_sec(public_pair))

def get_address_of_pubkey(pubkey):
    public_pair=encoding.sec_to_public_pair(encoding.binascii.unhexlify(pubkey))
    return encoding.public_pair_to_bitcoin_address(public_pair)

def get_nearby_valid_pubkey(pubkey):
    valid_pubkey=pubkey
    l=len(pubkey)
    while not is_pubkey_valid(valid_pubkey):
        info("trying "+valid_pubkey)
        next=hex(int(valid_pubkey, 16)+1).strip('L').split('0x')[1]
        valid_pubkey = next.zfill(l)
    info("valid  "+valid_pubkey)
    return valid_pubkey

def is_valid_hash(h):
    if len(h) != 64:
        return None
    res=re.findall(r"[0-9a-fA-F]+", value)
    if len(res)==1 and res[0]==value:
        return h
    return None

def is_valid_bitcoin_address(value):
    value = value.strip()
    if re.match(r"[a-zA-Z1-9]{27,35}$", value) is None:
      return False
    version = get_bcaddress_version(value)
    if version != None:
        return True
    return False

def get_bcaddress_version(address):
  """ Returns None if address is invalid. Otherwise returns integer version of address. """
  addr = b58decode(address,25)
  if addr is None: return None
  version = addr[0]
  checksum = addr[-4:]
  vh160 = addr[:-4] # Version plus hash160 is what is checksummed
  h3=hashlib.sha256(hashlib.sha256(vh160).digest()).digest()
  if h3[0:4] == checksum:
      return ord(version)
  return None

def is_valid_bitcoin_address_or_pubkey(value):
    return is_valid_bitcoin_address(value) or is_pubkey_valid(value)

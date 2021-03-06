from __future__ import print_function

import re

from lib.settings import (
    DAGON_ISSUE_LINK,
    LOGGER,
    shutdown,
    hash_guarantee
)


# Has to be the first function so I can use it in the regex
def build_re(hex_len, prefix=r"", suffix=r"(:.+)?"):
    regex_string = r"^{}[a-f0-9]{{{}}}{}$".format(prefix, hex_len, suffix)
    return re.compile(regex_string, re.IGNORECASE)


# Top: Most likely algorithm
# Bottom: Least likely algorithm (may not be implemented)
HASH_TYPE_REGEX = {
    build_re(8, prefix="(0x)?", suffix="(L)?"): [
        ("crc32", None), (None, None)
    ],
    build_re(20): [
        ("half sha1", None), (None, None)
    ],
    build_re(32, prefix="(md5)?"): [
        ("md5", "md4", "md2", "ntlm", "postgresql",
         "md5(md5(pass)+md5(salt))", "md5(md5(pass))", "md5(salt+pass+salt)",
         "md5(md5(md5(pass)))"),
        ("ripe128", "haval128", "tiger128",
         "skein256(128)", "skein512(128)", "skype",
         "zipmonster", "prestashop")
    ],
    build_re(16, prefix="(0x)?", suffix="(L)?"): [
        ("half md5", "oracle 10g", "crc64"), (None, None)
    ],
    build_re(64): [
        ("sha256", "sha3_256"),
        ("haval256", "gost r 34.1194",
         "gost cryptopro sbox", "skein256", "skein512(256)",
         "ventrilo", "ripemd256")
    ],
    build_re(128): [
        ("sha512", "whirlpool", "sha3_512"),
        ("salsa10", "salsa20", "skein512",
         "skein1024(512)")
    ],
    build_re(54, prefix="0x0100", suffix=""): [
        ("mssql 2005", None),
        (None, None)
    ],
    build_re(56, suffix=""): [
        ("sha224", "sha3_224"),
        ("skein256(224)", "skein512(224)", "haval224")
    ],
    build_re(40): [
        ("sha1", "ripemd160", "sha1(rounds(pass))"),
        ("haval160", "tiger160", "has160",
         "skein256(160)", "skein512(160)", "dsa")
    ],
    build_re(96, suffix="", prefix="(0x0100)?"): [
        ("sha384", "sha3_384", "mssql 2000"), ("skein512(384)", "skein1024(384")
    ],
    build_re(40, prefix=r"\*", suffix=""):  [
        ("mysql", None), (None, None)
    ],
    build_re(48, suffix=""): [
        ("tiger192", None),
        ("haval192", "sha1(oracle)", "xsha v10.4-v10.6")
    ],
    re.compile("\A\$1\$.{1,8}\$[./a-zA-Z0-9]+\Z", re.IGNORECASE): [
        ("md5 crypt", None), (None, None)
    ],
    #re.compile(r"^\$\w+\$\w+(\$)?\w+(.)?$", re.IGNORECASE): [
    #    ("wordpress", None), ("Joomla", None)
    #],
    re.compile(r"^\$\d\w\$\d+\$\S{53}$", re.IGNORECASE): [
        ("blowfish", None), (None, None)
    ],
    re.compile(r"^S:[a-zA-Z0-9]{60}$", re.IGNORECASE): [
        ("oracle 11g", None), (None, None)
    ],
    re.compile(r"^[0-9a-z]{4,12}:[0-9a-f]{16,20}:[0-9a-z]{2080}$", re.IGNORECASE): [
        ("agile", None), (None, None)
    ],
    re.compile(r"^[0-9a-f]{64,70}:[a-f0-9]{32,40}:\d+:[a-f0-9]{608,620}$", re.IGNORECASE): [
        ("cloud", None), (None, None)
    ],
    re.compile(r"^\{SSHA\S+$", re.IGNORECASE): [
        ("ssha", None), (None, None)
    ],
    re.compile(r"^\w+:\d+:[a-z0-9]{32}:[a-z0-9]{32}:::$", re.IGNORECASE): [
        ("windows local (ntlm)", None), (None, None)
    ]
}


def verify_hash_type(hash_to_verify, least_likely=False, verbose=False):
    """
      Attempt to verify a given hash by type (md5, sha1, etc..)

      >  :param hash_to_verify: hash string
      >  :param least_likely: show least likely options as well
      >  :return: likely options, least likely options, or none

      Example:
        >>> verify_hash_type("098f6bcd4621d373cade4e832627b4f6", least_likely=True)
        [('md5', 'md4', 'md2'), ('double md5', 'lm', ... )]
    """
    for regex, hash_types in HASH_TYPE_REGEX.items():  # iter is not available in Python 3.x
        if verbose:
            LOGGER.debug("Testing: {}".format(hash_types))
        if regex.match(hash_to_verify):
            return hash_types if least_likely else hash_types[0]
    error_msg = (
        "Unable to find any algorithms to match the given hash. If you "
        "feel this algorithm should be implemented make an issue here: {}")
    LOGGER.fatal(error_msg.format(DAGON_ISSUE_LINK))
    # hash_guarantee(hash_to_verify)
    LOGGER.warning("`hash_guarantee` has been turned off for the time being")
    shutdown(1)

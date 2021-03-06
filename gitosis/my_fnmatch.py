"""Filename matching with shell patterns.

fnmatch(FILENAME, PATTERN) matches ignore case.
fnmatchcase(FILENAME, PATTERN) always takes case in account.

The functions operate by translating the pattern into a regular
expression.  They cache the compiled regular expressions for speed.

The function translate(PATTERN) returns a regular expression
corresponding to PATTERN.  (It does not compile it.)

Double or multiple stars has special meaning: include any characters
including the path seperater '/', while single star matches characters
except '/'.  -- Hacked by Jiang Xin. <jiangxin AT ossxp.com>
"""

import re

__all__ = ["filter", "fnmatch","fnmatchcase","translate"]

_cache = {}

def fnmatch(name, pat):
    """Test whether FILENAME matches PATTERN.

    Patterns are Unix shell style:

    *       matches everything except '/'
    **      matches everything including '/'
    ?       matches any single character
    [seq]   matches any character in seq
    [!seq]  matches any char not in seq

    An initial period in FILENAME is not special.
    Both FILENAME and PATTERN are case-insensitive.
    If you don't want this, use fnmatchcase(FILENAME, PATTERN).

    Example:

    >>> fnmatch("My/Repos", "m**")
    True
    >>> fnmatch("My/Repos", "*m**")
    True
    >>> fnmatch("My/Repos", "*Y**s")
    True
    >>> fnmatch("My/Repos", "*Y**x")
    False
    >>> fnmatch("My/Repos", "My/Repo")
    False
    >>> fnmatch("MyRepos", "MyRepo")
    False
    >>> fnmatch("My/Repos", "m*")
    False
    """

    import os
    name = name.lower()
    pat = pat.lower()
    return fnmatchcase(name, pat)

def filter(names, pat):
    """Return the subset of the list NAMES that match PAT"""
    import os,posixpath
    result=[]
    pat=os.path.normcase(pat)
    if not pat in _cache:
        res = translate(pat)
        _cache[pat] = re.compile(res)
    match=_cache[pat].match
    if os.path is posixpath:
        # normcase on posix is NOP. Optimize it away from the loop.
        for name in names:
            if match(name):
                result.append(name)
    else:
        for name in names:
            if match(os.path.normcase(name)):
                result.append(name)
    return result

def fnmatchcase(name, pat):
    """Test whether FILENAME matches PATTERN, including case.

    This is a version of fnmatch() which doesn't case-normalize
    its arguments.

    Example:

    >>> fnmatchcase("My/Repos", "M**")
    True
    >>> fnmatchcase("My/Repos", "m**")
    False
    >>> fnmatchcase("My/Repos", "*m**")
    False
    >>> fnmatchcase("MyRepos", "MyRepo")
    False
    """

    if not pat in _cache:
        res = translate(pat)
        _cache[pat] = re.compile(res)
    return _cache[pat].match(name) is not None

def translate(pat):
    """Translate a shell PATTERN to a regular expression.

    There is no way to quote meta-characters.
    """

    i, n = 0, len(pat)
    multistars = False
    res = ''
    while i < n:
        c = pat[i]
        i = i+1
        if c == '*':
            while i < n:
                c = pat[i]
                if c != '*': 
                    break
                i = i+1
                multistars = True
            if multistars:
                res = res + '.*'
            else:
                res = res + '[^/]*'
        elif c == '?':
            res = res + '.'
        elif c == '[':
            j = i
            if j < n and pat[j] == '!':
                j = j+1
            if j < n and pat[j] == ']':
                j = j+1
            while j < n and pat[j] != ']':
                j = j+1
            if j >= n:
                res = res + '\\['
            else:
                stuff = pat[i:j].replace('\\','\\\\')
                i = j+1
                if stuff[0] == '!':
                    stuff = '^' + stuff[1:]
                elif stuff[0] == '^':
                    stuff = '\\' + stuff
                res = '%s[%s]' % (res, stuff)
        else:
            res = res + re.escape(c)
    return res + "$"

if __name__ == "__main__":
    import doctest
    doctest.testmod( )

# vim: et sw=4 ts=4

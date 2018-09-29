"""
This module reads a simple Variables file in text form
and popullates a the macro dictionary
"""


import os
import sys
import re

from .envmacros import MacroLookup
from .envmacros import MacroResult

__all__ = ['MacroSyntax', 'MacroDuplicate', 'read_text_varfile' ]

class MacroSyntax( Exception ):
    pass

class MacroDuplicate( Exception ):
    pass
    
_re_macro = re.compile( r'^\s*(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?P<value>.*)$' )

def read_text_varfile( filename, lookup ):
    assert( isinstance( lookup, MacroLookup ) )
    result = MacroResult()
    
    # slurp the lines
    with open( filename, 'r' ) as f:
        lines = f.read().splitlines()
    
    # parse the lines
    for lineno, line in enumerate( lines ):
        # 1 based, not 0 based
        lineno += 1
        line = line.strip()
        if len(line) == 0:
            continue
        if line[0] == '#':
            continue
        # look for macros
        m = _re_macro.match( line )
        if m == None:
            raise MacroSyntax( "%s:%d: syntax: %s" % (filename,lineno,line))
        n = m.group('name')
        v = m.group('value')
        v = v.strip()
        w = '%s:%d' % (filename,lineno)
        existing = lookup.lookup( result, n )
        if existing != None:
            msg = "%s:%s: Duplicate %s, previous: %s" % (filename,lineno,n, result.where )
            raise MacroDuplicate(msg) 
            
        lookup.add( n,v, w )
    

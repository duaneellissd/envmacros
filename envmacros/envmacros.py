
import re
import os
import time
import math
import sys
from frozenclass import FrozenClass

# We don't specifically use 'math'
# but by importing this you can use
# things like math.cos() and sin() in expressions.

from math import *

__all__ = ['MacroError',
           'MacroLookup',
           'MacroResolver',
           'MacroResult',
           'ExpressionEvaluator',
           'lookup',
           'resolver',
           'evaluator'
]


# this regex matches a C (or bash) style symbol, in the form: ${NAME}
# the 3 matched named groups are 
#    "before" - stuff before the invocation.
#    "name" - the name of the macro
#    "after" - the text after the macro
_re_symbol = re.compile( "^(?P<before>.*)\$\{(?P<name>[A-Za-z_][0-9A-Za-z_]*)\}(?P<after>.*)$" )

DEBUG=False

class MacroError( Exception ):
    pass

if sys.version_info[0] == 2:
    _str_able_types = (int, float,long )
else:
    _str_able_types = (int, float)


@FrozenClass
class MacroLookup( object ):
    """
    This represents a basic macro lookup class
    that holds your macro variable names.
    """
    def __init__(self, allow_env = True):
        self.entries = dict()
        self.allow_env = allow_env
        self.parent    = None

    def set_parent( self, parent ):
        self.parent = parent

    def add( self, name, value, where = None ):
        """
        Add a name value pair.
        With an optional location (ie: where defined)
        """
        
        if isinstance( value, _str_able_types ):
            value = str(value)
        assert( isinstance( value, str ) )
        self.entries[name] = (value, where)

    def lookup( self, result, name ):
        """
        Return the text (or none) for macro 'name'.
        """

        value = None
        where = None
        
        # is it in our dictonary?
        tuple_ = self.entries.get( name, None )
        if tuple_:
            value = tuple_[0]
            where = tuple_[1]

        # if not found
        if (value == None) and self.allow_env:
            value = os.environ.get( name, None )
            if value != None:
                where = "os.environ[%s]" % name

        # is it dynamic?
        if value == None:
            fname =  'macro_' + name
            func = getattr( self, fname, None)
            if func != None:
                where = "function: %s()" % fname
                try:
                    value = func( name, result )
                except Exception as e:
                    result.err_msg = "Exception: %s() -> %s" % (fname, str(e))
                    return None

        if value == None:
            result.err_msg = "Undefined: %s" % name
            return None
        
        if where != None:
            result.add_step("%s: %s -> %s" % (where, name, value))
        else:
            result.add_step("%s -> %s" % (name,value))
        return value

    def macro_NOW(self, name, result):
        """
        This handles the macro ${NOW}
        """
        return time.ctime()

    def macro_GETCWD(self, name, result):
        """
        This handles the macro ${GETCWD}
        """
        return os.getcwd()

# our global "macros"
lookup = MacroLookup()
    
@FrozenClass
class MacroResult(object):
    """
    A macro resolution result.
    The resulting transformation is found in self.result.
    
    If self.result is None, then see self.err_msg.
    Additional debug information can be found in self.steps
    """
    PASS_MAX = 50
    def __init__(self):
        self.pass_count = 0
        self.pass_max   = self.PASS_MAX
        self.err_msg = None
        self.result = None
        self.steps = []

    def add_step( self, txt ):
        self.steps.append( txt )

@FrozenClass
class MacroResolver(object):
    """
    Evaluate a string, replacing all ${macros} with their values.
    Returns a MacroResult()
    """
    def __init__(self, my_lookup = None ):
        self.result = None
        if my_lookup == None:
            global lookup
            my_lookup = lookup
        assert( isinstance( my_lookup, MacroLookup ) )
        self.lookup = my_lookup
        self.lookup.set_parent( self )

    def resolve( self, text, result=None ):
        """
        Given text, resolve all macros.
        """
        if result == None:
            result = MacroResult()
        result.add_step("start: %s" % text )
        result.err_msg = None
        result.result  = text

        # ALL macros have $ signs.
        if '$' not in result.result:
            # if no $ signs occur.. we are done
            return result
        
        while self._make_pass(result):
            result.pass_count += 1
            if result.pass_count > result.pass_max:
                result.add_step("too many passes")
                result.err_msg = "Too many passes"
                break
            result.add_step("pass: %d -> %s" % (result.pass_count, result.result))
        # if an error occurred
        if result.err_msg != None:
            # do not return text.
            result.result = None
        return result

    def _make_pass(self, result):
        # FUTURE: support function like macros
        # for example:  ${str.upper(${foo})}
        
        # Make a single pass over the string resolving macros.
        m = _re_symbol.match( result.result )
        if m is None:
            # no macro invocation found
            return False

        mname = m.group('name')
        if DEBUG:
            result.add_step("text-before='%s'" % m.group('before'))
            result.add_step("macro: %s" % mname )
            result.add_step("text-after='%s'" % m.group('after'))
        
        txt = self.lookup.lookup( result, mname )
        if txt == None:
            return False
        result.result = m.group('before') + txt + m.group('after')
        result.add_step("New: %s" % result.result )
        return True

resolver = MacroResolver(lookup)

# match hex numbers
_re_hex = re.compile('0[xX][0-9a-fA-F]+')

# what strings are ok in our restricted number only modemode?
_ok_whitelist = set()
_ok_whitelist.add('True')
_ok_whitelist.add('False')
_ok_whitelist.add('and')
_ok_whitelist.add('or')
_ok_whitelist.add('not')
# All functions in math
for tmp in dir(math):
    if tmp[0] != '_':
        tmp = tmp + '('
        _ok_whitelist.add(tmp)

# digits or numbers
_re_digits  = re.compile(  r'^[0123456789.]+$')

# these are chars we can ignore
# or safely transform to spaces
_str_from = "-+*/&|%!~<>=.)"
_str_to   = "              "

try:
    # Python > 3.1
    _table_to_space = str.maketrans( _str_from, _str_to )
except:
    # Python < 3.1
    import string
    _table_to_space = string.maketrans( _str_from, _str_to )

def _safe_eval_check( text ):
    ''' 
    Returns None if the string is ok to eval.

    Returns an error message if the string is not safe to eval.

    The technique is generally replace safe things with spaces
    Then split the string on spaces and deal with each possbile
    thing we might find - we are not checking syntax here.
    We let python handle the syntax.
    '''
    
    # Python allows spaces between the function
    # and the opening parens we need to fix that.
    # for example:  "cos   (123)" we must
    # convert this into "cos(123)"

    oldlen = len(text)
    while True:
        # replace what we can
        text = text.replace( ' (', '(' )
        # If any change occurs, our string is shorter
        newlen = len(text)
        if oldlen == newlen:
            # no change, we are done
            break
        # Try again
        oldlen = newlen


    # Now, we might have a string like this:
    # For example:   "cos(123)*(4 >= ~123) && False < 7"
    #
    # What matters to us is is the "cos(" part that could
    # instead be some evilfunction() call.

    # We need to seperate cos(123) into: "cos( 123 )"
    # by adding spaces we can use str.split() to parse.
    #
    text = text.replace( '(', '( ')

    # our string is now something like this:
    # And we can throw away all of our math operators.
    #
    # old: "cos(123)*(4 >= ~123) && False < 7"
    # new: "cos( 123   4     123     False   7"
    text = text.translate( _table_to_space )

    # we have a white list of function names.
    # we can check each part of the new string
    # against our white list of function names.
    for part in text.split( ' ' ):

        # ignore blanks
        if len(part)==0:
            continue

        if part == '(':
            # this happens in simple expressions
            continue
        
        # Most common will be pure digits.
        m = _re_digits.match( part )
        if m != None:
            continue

        # Allow hex digits
        m = _re_hex.match( part )
        if m != None:
            continue

        # We have something..
        # It could be: "True" or "False"
        # It could be a function call, like: "cos("
        # or the start some "evil(" function call.
        #
        # Check it against our white list of function calls.
        if part in _ok_whitelist:
            # good
            continue
        
        # Not recognized
        return "Illegal: %s" % part
    # nothing bad found
    return None

@FrozenClass
class ExpressionEvaluator( object ):
    '''
    Given a string, which may contain macros
    and should contain an expression of some sort..
    
    Evaluate the expression and return the result.
    '''

    def __init__(self, macro_resolver = None):
        if macro_resolver == None:
            # it is our default value
            global resolver
            macro_resolver = resolver
        assert( isinstance( resolver, MacroResolver ) )
        self.resolver = macro_resolver
        
    def eval( self, text, result = None ):
        
        result = self.resolver.resolve( text, result )
        if result.err_msg != None:
            result.result = None
            return result

        if result.result != text:
            result.add_step("Evalutate: '%s'" % result.result)

        result.result = result.result.strip()
        if len( result.result ) == 0:
            result.err_msg = "Empty string?"
            result.result = None
            return result
            
        # is the numeric value safe?
        result.err_msg = _safe_eval_check( result.result )
        if result.err_msg != None:
            result.result = None
            return result

        # let python do the math
        try:
            r = eval( result.result )
            result.result = r
        except Exception as e:
            result.add_step("Exception: %s" % str(e) )
            result.err_msg = "Syntax Error: %s" % str(e)
            result.result = None

        if result.err_msg != None:
            result.result = None
            
        return result

evaluator = ExpressionEvaluator( resolver )


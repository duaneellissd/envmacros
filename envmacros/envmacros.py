
import re
import os
import time

__all__ = ['MacroError','MacroDictionary','MacroResolver','MacroResult']


# this regex matches a C (or bash) style symbol, in the form: ${NAME}
# the 3 matched named groups are 
#    "before" - stuff before the invocation.
#    "name" - the name of the macro
#    "after" - the text after the macro
c_symbol = re.compile( "^(?P<before>.*)\$\{(?P<name>[A-Za-z_][0-9A-Za-z_]*)\}(?P<after>.*)$" )

DEBUG=False

class MacroError( Exception ):
    pass

class MacroDictionary( object ):
    """
    This represents a basic dictionary like object
    that holds your macro variable names.
    """
    def __init__(self, allow_env = True):
        self.entries = dict()
        self.allow_env = allow_env
        self.parent    = None

    def set_parent( self, parent ):
        self.parent = parent
        
    def add( self, name, value ):
        """
        Add a name value pair.
        """
        self.entries[name] = value

    def lookup( self, result, name ):
        """
        Return the text (or none) for macro 'name'.
        """
        value = self.entries.get( name, None )
        if value != None:
            return value
        if self.allow_env:
            value = os.environ.get( name, None )
            if value != None:
                return value
        # dynamic?
        func = getattr( self, 'macro_' + name, None)
        if func is None:
            return None
        return func( name )

    def macro_NOW(self):
        """
        This handles the macro ${NOW}
        """
        return time.ctime()

    def macro_GETCWD(self):
        """
        This handles the macro ${GETCWD}
        """
        return os.getcwd()

class MacroResult(object):
    """
    A macro resolution result.
    The resulting transformation is found in self.result.
    
    If self.result is None, then see self.err_msg.
    Additional debug information can be found in self.steps
    """
    def __init__(self):
        self.err_msg = None
        self.done = False
        self.result = None
        self.steps = []

    def add_step( self, txt ):
        self.steps.append( txt )

class MacroResolver(object):
    def __init__(self, lookup = None ):
        self.result = None
        self.pass_max   = 50
        self.pass_count = 0
        if lookup == None:
            lookup = MacroDictionary()
        self.lookup = lookup
        self.lookup.set_parent( self )

    def resolve( self, text ):
        """
        Given text, resolve all macros.
        """
        self.pass_count = 0
        self.result = MacroResult()
        self.result.add_step("start: %s" % text )
        self.result.result = text
        while self._make_pass():
            self.pass_count += 1
            if self.pass_count > self.pass_max:
                self.result.add_step("too many passes")
                self.result.err_msg = "Too many passes"
                break
            self.result.add_step("pass: %d -> %s" % (self.pass_count, self.result.result))
        r = self.result
        self.result = None
        # if an error occurred
        if r.err_msg != None:
            # do not return text.
            r.result = None
        return r

    def _make_pass(self):
        # Make a single pass over the string resolving macros.
        m = c_symbol.match( self.result.result )
        if m is None:
            # no invocation found
            # FUTURE: support function like macros
            # for example:  ${str.upper(${foo})}
            return False
        name = m.group('name')
        result = self.lookup.lookup( self.result, name )
        if result == None:
            self.result.err_msg = "Undefined: %s" % name
            return False
        self.result.result = m.group('before') + result + m.group('after')
        if DEBUG:
            self.result.add_step("${%s}->%s" % (name, result))
            self.result.add_step("before='%s'" % m.group('before'))
            self.result.add_step("after='%s'" % m.group('after'))
            self.result.add_step("New: %s" % self.result.result )
        return True


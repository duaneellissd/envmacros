from unittest import TestCase
import sys
import envmacros
import os

# change this to debug things
VERBOSE=False

def my_print( s ):
    if VERBOSE:
        print(s)

def create_resolver():
    resolver = envmacros.MacroResolver()
    resolver.lookup.add('Foo','Bar')
    resolver.lookup.add( 'child', 'Zack' )
    resolver.lookup.add( 'parent_Zack', 'duane')
    resolver.lookup.add( 'dog', 'Dolly')
    resolver.lookup.add( 'A', '${B}')
    resolver.lookup.add( 'B', '${C}')
    resolver.lookup.add( 'C', '${D}')
    resolver.lookup.add( 'D', '${A}')
    resolver.lookup.add( "seven", "7" )
    resolver.lookup.add( "one", "1" )
    resolver.lookup.add( "bad_two", "1+{$one}" )
    resolver.lookup.add( "should_have_parens", "5-4" )
    resolver.lookup.add( "good_two", "(1+${one})" )
    resolver.lookup.add( "cos0", "cos(0)")
    resolver.lookup.add( "cospi", "cos(3.14159)")
    resolver.lookup.add( "four", "(2*${good_two})")
    resolver.lookup.add( "ref_undef", "${undefined_thing}" )
    resolver.lookup.add( "bad_macro", "${bad_macro" )
    return resolver

def create_eval():
    r = create_resolver()
    e = envmacros.ExpressionEvaluator( r )
    return e

def print_result( r ):
    my_print("")
    my_print("==========================")
    s = r.result
    if s == None:
        t = "None"
        s = "(none)"
    else:
        t = s.__class__.__name__
    my_print(" result: (%s) '%s'" % (t,s) )
    s = r.err_msg
    if s == None:
        s = "(none)"
    my_print("err_msg: '%s'" % s )
    for n,s in enumerate( r.steps ):
        my_print( "%2d) %s" % (n,s))
    my_print("==========================")
    

class MyTest( TestCase ):
    def flush(self):
        sys.stdout.flush()
        sys.stderr.flush()
    def setUp(self):
        self.flush()
        
    def tearDown(self):
        self.flush()
                
    def check_result( self, f, t ):
        self.flush()
        my_print("")
        my_print("From: %s" % f)
        my_print("  To: %s" % t)
        resolver = create_resolver()
                
        r = resolver.resolve( f )
        self.assertEqual( r.err_msg, None )
        if t == r.result:
            my_print("ok")
            return
        my_print("========================")
        my_print("Expected: '%s'" % t)
        my_print("========================")
        print_result(result)
        my_print("========================")
        self.flush()

    def test_010(self):
        self.check_result( '', '' )     
                
    def test_020(self):
        self.check_result(  'duane', 'duane' )
                
    def test_030(self):
        self.check_result(  '${dog}', 'Dolly' )
    def test_040(self):
        self.check_result(  ' ${dog}', ' Dolly' )
    def test_050(self):
        self.check_result(  ' ${dog} ', ' Dolly ' )
    def test_060(self):
        self.check_result(  'abc->${dog}<-xyz' , 'abc->Dolly<-xyz' )
    def test_070(self):
        self.check_result(  'Double ${parent_${child}}', 'Double duane')
                
    def test_080(self):
        # Missing closing brace
        self.check_result( 'Borked ${parent_${child}', 'Borked ${parent_Zack' )
            
    def test_090(self):
        r = create_resolver()
        mr = r.resolve('${not_found}')
        self.assertEqual( mr.result, None )
        self.assertNotEqual( mr.err_msg, None )
                
    def test_100(self):
        r = create_resolver()
        result = envmacros.MacroResult()
        result.pass_max = 15
        mr = r.resolve( 'recursive ${A} for ever', result )
        self.assertEqual( mr.result, None )
        self.assertNotEqual( mr.err_msg, None )
        print_result(mr)

    def eval_xx( self, str_expr ):
        self.flush()
        my_print("EVAL: %s" % str_expr)
        r = create_eval()
        result = r.eval( str_expr )
        print_result(result)
        my_print("Check result")
        return result
        
    def eval_bad( self, str_expr ):
        result = self.eval_xx( str_expr )
        bad = False
        if result.result == None:
            my_print("GOOD: result is none")
        else:
            my_print("WRONG: result should be None, it is: '%s'" % result.result)
            bad =True
        if result.err_msg == None:
            my_print("WRONG: err_msg is None, it should have value")
            bad = True
        else:
            my_print("GOOD: err_msg = %s" % result.err_msg )
        if bad:
            self.fail()
        else:
            # self.success()
            pass

    def eval_good( self, expect, str_expr):
        self.flush()
        result = self.eval_xx( str_expr )
        my_print("============================")
        my_print("Expected: %d" % expect )
        my_print("============================")
        bad = False
        if result.err_msg == None:
            my_print("Good: err_msg is None")
        else:
            my_print("WRONG: err_msg is not None, it is: '%s'" % result.err_msg )
            bad =True
        my_print("errmsg ok")
        v = 0
        if result.result is None:
            bad =True
            my_print("WRONG: result is none!")
        else:
            v = result.result
            my_print("GOOD: Result is not none, it is '%s'" % v )
        if not bad:
            if isinstance( v, int ):
                my_print("GOOD: Result is type int()")
            else:
                if isinstance(v,float) and (v == 1.0):
                    # Then this is good
                    my_print("OK 1.0 is a float")
                else:
                    bad = True
                    my_print("WRONG: result is not type int it is: %s" % v.__class__.__name__ )

        if not bad:
            if expect == v:
                return
            bad = True
            my_print("WRONG: Expect %s" % expect )
            my_print("WRONG:    got %s" % v ) 
        self.flush()
        if bad:
            self.fail()
        else:
            # good
            pass
    def test_200(self):
        self.eval_bad( "" )

    def test_210(self):
        self.eval_bad( "dog")
                         
    def test_210(self):
        self.eval_bad( "3 * - / 4" )

    def test_210(self):
        self.eval_bad( "${not_defined_macro}" )

    def test_210(self):
        self.eval_good( 1, "1" )

    def test_210(self):
        self.eval_good( 4, "1 + 1 + 1 + 1" )
        
    def test_210(self):
        self.eval_good( 4, "1 + 1 + ${one} + 1" )
        

    def test_215( self ):
        self.eval_good( 4, "2 * ${good_two}")

    def test_216( self ):
        self.eval_bad( "2 * ${bad_two}")
        
    def test_217( self ):
        # this is 2 * 5-4, or (2*5)-4, which is 6
        self.eval_good( 6, "2 * ${should_have_parens}")

    def test_220( self ):
        self.eval_good( 1, "2 / (${good_two})")

    def test_230( self ):
        self.eval_good( True, "True")
        
    def test_231( self ):
        self.eval_good( True, "False!=True")
    def test_232( self ):
        self.eval_good( True, "False !=  True")
    def test_233( self ):
        self.eval_good( True, "  False !=  True  ")
                         

    def test_240( self ):
        r = create_eval()
        mr = r.eval("cos(0)")
        self.assertTrue( mr.result != None ) 
        self.assertTrue( mr.err_msg == None )
        self.assertTrue( mr.result, 1 )

    def test_250(self):
        self.eval_good(    1,   "${one}" )
    def test_251(self):
        self.eval_good( 0x0100,  "${one}<<(2*${four})")
    def test_252(self):
        self.eval_good( 0x0100,  "((0x0100 & (${one}<<(2*${four}))))")
    def test_253(self):
        self.eval_good( True,   "((0x0100 & (${one}<<(2*${four}))) != 0)")
    def test_254(self):
        self.eval_good( True,   "((0x0100 & (${one}<<(2*${four}))) != 0) == True"  )

    def test_255(self):
        self.eval_good( True,   "True and True" )

    def test_256(self):
        self.eval_good( True,   "True and not False")

    def test_257(self):
        # Like: C's (!!x)
        self.eval_good( 1,   "not not 7")

        

    def test_300_parse_bad_lookup(self):
        class Foo():
            pass
        with self.assertRaises( Exception ):
            envmacros.read_text_varfile( "asfa12357VDE_does_not_eixst", Foo() )

    def test_310_nofile( self ):
        lookup = envmacros.MacroLookup()
        
        with self.assertRaises(FileNotFoundError):
            envmacros.read_text_varfile( "asfa12357VDE_does_not_eixst", lookup )
    
    def test_320_good_file( self ):
        fn = os.path.join( os.path.dirname( __file__ ), 'test_var_file_good.txt' )
        
        lookup = envmacros.MacroLookup()
        envmacros.read_text_varfile( fn, lookup )
        # We should find a few vars
        
        r = envmacros.MacroResult()
        tmp = lookup.lookup(  r, 'NOT_FOUND_myvar1' )
        self.assertTrue( tmp == None )
        tmp = lookup.lookup(  r, 'myvar' )
        self.assertTrue( tmp != None )
        self.assertEqual( tmp , "SomeValue" )
        tmp = lookup.lookup( r, 'othervar' )
        self.assertEqual( tmp, 'ThisValue' )
        
    def test_330_syntax( self ):
        fn = os.path.join( os.path.dirname( __file__ ), 'test_var_file_syntax.txt' )
        
        lookup = envmacros.MacroLookup()
        with self.assertRaises( envmacros.MacroSyntax ):
            envmacros.read_text_varfile( fn, lookup )

        
    def test_340_dup( self ):
        fn = os.path.join( os.path.dirname( __file__ ), 'test_var_file_dup.txt' )
        
        lookup = envmacros.MacroLookup()
        with self.assertRaises( envmacros.MacroDuplicate ):
            envmacros.read_text_varfile( fn, lookup )

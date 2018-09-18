from unittest import TestCase
import sys

import envmacros


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
	return resolver

class MyTest( TestCase ):

	def setUp(self):
		sys.stdout.flush()
		sys.stderr.flush()
		
	def tearDown(self):
		sys.stdout.flush()
		sys.stderr.flush()
	
	def check_result( self, f, t ):
		print("")
		print("From: %s" % f)
		print("  To: %s" % t)
		resolver = create_resolver()
		
		r = resolver.resolve( f )
		self.assertEqual( r.err_msg, None )
		if t == r.result:
			print("ok")
			return
		print("========================")
		print("    From: '%s'" % f)
		print("Expected: '%s'" % t)
		print("  Actual: '%s'" % r.result)
		print("------------------------")
		for step in r.steps:
			print(step)
		self.fail('Wrong')
		print("========================")

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
		r.pass_max = 15
		mr = r.resolve( 'recursive ${A} for ever' )
		self.assertEqual( mr.result, None )
		self.assertNotEqual( mr.err_msg, None )
		print(mr.result)
		for step in mr.steps:
			print(step)
		

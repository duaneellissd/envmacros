"""
This module does simple Macro Transformation and lookup.

You can do things like:

	   define:	child=Zack
	   define:	parent_Zack = Duane

Then resolve text like: ${parent_${child}}, and get Duane.

Some macros are Dynamic ... for example ${NOW} is the current
date and time, and ${GETCWD} is the current directory.

Macro names:
	Follow the C (and Python) variable name rules.
	The first symbol must be a letter (A-Z, or a-z) or an underline(_)
	After the first symbol, digits are allowed.

Some names are automatically discovered and processed

Example:

	import envmacros
	
	resolver = envmacros.MacroResolver()
	
	resolver.lookup.add('color', 'blue')
	
	result = resolver.resolve( 'The color is: ${color} today' )
	if result.err_msg:
		print(result.err_msg)
		# for detailed errors
		for step in result.steps:
			print( step )

Also see the function:
	import envmacros
	
	global_mylookup = envmacros.lookup
	# or  my_lookup = envmacros.MacroLookup()
	
	# read macros from a file
	envmacros.read_text_varfile( "somefilename.txt", my_lookup )
"""


from .envmacros import *
from .text_varfile import *

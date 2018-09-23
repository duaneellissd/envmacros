# Simple shell script macro resolution.

## Where this is useful

You are reading a configuration file, or other data file and the
content of that file would benifit from being able to reference
variables like ${FOO} or ${BAR} and have those magic strings transform

## Examples Simple text

Given a simple list of macros and values, such as:

* `child=Zack`
* `parent_Zack=Duane`
	
Do simple text transformations like:  
* Hello `${child}` -> Zack
* Hello `${parent_${chiid}}` -> Duane

## Examples - Numerical Expressions

Given tehse macros:
* `one = 1`
* `two = (${one} + ${one})`
* `four = (${two} * ${two})`

All basic Python basic and advanced operations are supported
* `this_is_true = ((0x0100 & (${one}<<(2*${four}))) != 0) == True`


## To install from git hub:

```bash
bash$ pip install git+https://github.com/duaneellissd/envmacros.git
```
   
Or, download a zip file
   
```bash
bash$ pip install envmacros.zip
```

# Example usage:(macros)

```python
import envmacros

# Create a private thing to hold macros
# We could have used the "quasi-globals"
#    envmacros.lookup   => a common MacroLookup() class
#    envmacros.resolver => a common MacroResolver() class
resolver = envmacros.MacroResolver()
   
resolver.lookup.add("child", "Zack")
resolver.lookup.add("parent_Zack", "Duane")
   
# this does not fail
result = resolver.resolve( "The ${child}")
print( result.result )
   
# example of an error
result = resolver.resolve( "The ${CHiLD}")
if result.err_msg != None:
    print("Error message: " + result.err_msg )
    # If you choose to have more detail...
    for this_step in result.steps:
        print( this_step )
```

# Example Usage, Expressions

```python
import envmacros

# Add a macro indicating it came from a file....
envmacros.lookup.add( "one", 1, "foobar.data:23" )
# Do not specify where it came from, Default where=None
envmacros.lookup.add( "two", "(${one} + ${one})" )

result = envmacros.evaluator.eval( "7 * 2 * (${one} + ${two})" )
if result.err_msg != None:
    print("My math fails me")
else:
    print("Result: %d" % result.result )
    if result.result == 42:
        print("We have an answer")
    else:
        print("Deep thougth is broken!")
# you can also see the steps the evaluation went through
for s in result.steps:
    print("s = %s" % s)
```


# Changes

* 1.0 - Initial release, expressions
* 2.0 - Add simple arithmatic expressions, Rename: MacroDictionary() ->MacroLookup()

# Future:
 
Macros like  

```bash
${os.path.dirname(${FOOBAR})}
```

Which takes a variable `${FOOBAR}` evalutes it, then passes the 
result to `os.path.dirname()` - and can easily be extended to many
other standard (or custom) python functions.

It's not that hard ... did it before in a previous life 
and this feature was very handy..
	

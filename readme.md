# Simple shell script macro resolution.

Given a simple list of macros and values, such as:

* `child=Zack`
* `parent_Zack=Duane`
	
Do simple text transformations like:  
* Hello `${child}` -> Zack
* Hello `${parent_${chiid}}` -> Duane

# Where used

You are reading a configuration, or other data file and the
content of that file would benifit from being able to reference
variables like ${FOO} or ${BAR} and have those magic strings transform

## To install from git hub:

```bash
bash$ pip install git+https://github.com/duaneellissd/envmacros.git
```
   
Or, download a zip file
   
```bash
bash$ pip install envmacros.zip
```

# Example usage:

```python
import envmacros
   
resolver = envmacros.MacroResolver()
   
resolver.lookup.add("child", "Zack")
esolver.lookup.add("parent_Zack", "Duane")
   
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
	

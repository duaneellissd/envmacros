
from setuptools import setup

setup( name='envmacros',
       version='2.0',
       description='A simple module that supports Environment like macros.',
       long_description='Simple macro transformations like: ${parent_${child}} -> ${parent_Zack} -> Duane, including expressions',
       url='http://github.com/duaneellissd/envmacros',
       author='Duane Ellis',
       author_email='duane@duaneellis.com',
       keywords=['macro', 'variables', 'shell-environment', 'expressions' ],
       license='PSF - Same as Python',
       platforms='any',
       test_suite='tests',
       packages=['envmacros'],
       install_requires=[
           'frozenclass>=1'
           ]
)


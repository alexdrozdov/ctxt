"""
Ctxt - Semantic Call Stack Context Manager

Provides:
    * actual variable values for decorated stacktrace when exception occures
    * provides actions described with context manager

Example:
    >> @Tracer.traced('Adding {param1}, {param2}')
    >> def sum(self, v1, v2):
    >>     with Tracer.scope({'param1': v1 + 2, 'param2': v2 + 2}
    >>         a = {1: 2, 2: 4}
    >>         b = a[10]       # Here is KeyError exception raised
    >>         return v1 + v2
    >>
    >> sum(1, 2)

    This will throw StackTracerException with message `Adding 3 and 4`.
    Values for message format will be extracted from internal scope
    exception values map

"""
try:
    from distutils.core import setup
except ImportError:
    from setuptools import setup


setup(
    name='Ctxt',
    version='0.0.1-dev',
    url='http://github.com/alexdrozdov/ctxt',
    license='UNLICENSE',
    author='Alex Drozdov',
    author_email='alex.drozdovs@gmail.com',
    description='Semantic call stack context tracker',
    long_description=__doc__,
    packages=['ctxt'],
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=[],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: Public Domain',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Topic :: Utilities'
    ],
)

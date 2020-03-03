import pytest

import inspect
import rpy2_R6.R6 as r6
import rpy2.rinterface as ri
import rpy2.robjects as ro


def _list_names(obj):
    if obj is ro.NULL:
        return tuple()
    else:
        return tuple(obj.names)


@pytest.mark.parametrize(
    'callparams,pub_method_names,pub_field_names',
    (
        ('', tuple(), tuple()),
        ('public = list(x = function() {123}, y = "a")', ('x',), ('y',))
    )
)
def test_R6StaticClassWrapper(
        callparams, pub_method_names, pub_field_names):
    # Without custom conversion, R6ClassGenerator objects
    # are just environments.
    env = ro.r('R6Class("foo", {})'.format(callparams))
    assert isinstance(env, ri.SexpEnvironment)
    clsi = r6.R6StaticClassGenerator(env)
    assert clsi.classname[0] == 'foo'
    assert all(x in _list_names(clsi.public_methods) for x in pub_method_names)
    assert all(x in _list_names(clsi.public_fields) for x in pub_field_names)


@pytest.mark.parametrize(
    'rcode,classhierarchy,attributes',
    (
        ("""
        R6Class('Foo', public = list(x = function(x) { x * 2 }))
        """, ('Foo', 'R6'), ('x',)),
        ("""
        Bar <- R6Class('Bar', public = list(x = function(x) { x * 2 }))
        R6Class('Foo', inherit = Bar, public = list(y = function(x) { x + 1 }))
        """, ('Foo', 'Bar', 'R6'), ('x', 'y'))
    )
)
def test_R6DynamicClassWrapper(rcode, classhierarchy, attributes):
    clsgen = r6.R6DynamicClassGenerator(
        ro.r(rcode)
    )
    assert (tuple(cls.__name__ for cls in inspect.getmro(clsgen.new))[:-2]
            ==
            classhierarchy)
    r6instance = clsgen.new()
    assert all(hasattr(r6instance, a) for a in attributes)


def test_isr6classgenerator():
    clsi = ro.r('R6Class("Foo", public = list(x = function(x) { x * 2 }))')
    assert r6.is_r6classgenerator(clsi)

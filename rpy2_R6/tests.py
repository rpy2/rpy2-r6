import pytest

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


def test_R6DynamicClassWrapper():
    clsi = r6.R6DynamicClassGenerator(
        ro.r('R6Class("Foo", public = list(x = function(x) { x * 2 }))')
    )
    r6instance = clsi.new()
    assert all(hasattr(r6instance, x) for x in ('x'))
    type(r6instance).__name__ = 'Foo'


def test_isr6classgenerator():
    clsi = ro.r('R6Class("Foo", public = list(x = function(x) { x * 2 }))')
    assert r6.is_r6classgenerator(clsi)

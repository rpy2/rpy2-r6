import pytest

import inspect
import rpy2_r6.r6a as r6a
import rpy2_r6.r6b as r6b
import rpy2.rinterface as ri
import rpy2.robjects as ro


def _list_names(obj):
    if obj is ro.NULL:
        return tuple()
    else:
        return tuple(obj.names)


def _test_attributes_r6a_cls(obj, pub_method_names, pub_field_names):
    assert all(x in _list_names(obj._public_fields) for x in pub_field_names)


def _test_attributes_r6a_instance(obj, pub_method_names, pub_field_names):
    assert all(hasattr(obj, x) for x in pub_field_names)


def _test_attributes_r6b(obj, pub_method_names, pub_field_names):
    assert all(x in _list_names(obj.public_methods) for x in pub_method_names)
    assert all(x in _list_names(obj.public_fields) for x in pub_field_names)


@pytest.mark.parametrize(
    'constructor,classname_getter, test_attributes',
    ((r6a.R6Class, lambda x: x.class_name, _test_attributes_r6a_cls),
     (r6a.R6Class.from_robj, lambda x: x.class_name, _test_attributes_r6a_instance),
     (r6b.R6StaticClassGenerator, lambda x: x.classname[0], _test_attributes_r6b))
)
@pytest.mark.parametrize(
    'callparams,pub_method_names,pub_field_names',
    (
        ('', tuple(), tuple()),
        ('public = list(x = function() {123}, y = "a")', ('x',), ('y',))
    )
)
def test_R6StaticClassWrapper(
        constructor, classname_getter, test_attributes,
        callparams, pub_method_names, pub_field_names):
    # Without custom conversion, R6ClassGenerator objects
    # are just environments.
    env = ro.r('R6Class("foo", {})'.format(callparams))
    assert isinstance(env, ri.SexpEnvironment)
    clsi = constructor(env)
    assert classname_getter(clsi) == 'foo'
    test_attributes(clsi, pub_method_names, pub_field_names)


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
    clsgen = r6b.R6DynamicClassGenerator(
        ro.r(rcode)
    )
    assert (tuple(cls.__name__ for cls in inspect.getmro(clsgen.__R6CLASS__))[:-2]
            ==
            classhierarchy)
    r6instance = clsgen.new()
    assert all(hasattr(r6instance, a) for a in attributes)
    assert hasattr(r6instance, '__sexp__')


def test_isr6classgenerator():
    clsi = ro.r('R6Class("Foo", public = list(x = function(x) { x * 2 }))')
    assert r6b.is_r6classgenerator(clsi)

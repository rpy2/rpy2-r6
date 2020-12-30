import abc
import rpy2.rinterface
import rpy2.rinterface_lib._rinterface_capi as _rinterface
import rpy2.robjects
from rpy2.robjects.packages import (importr,
                                    WeakPackage)
import textwrap
import typing
import warnings
with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    R6_pack = importr('R6', on_conflict='warn')

TARGET_VERSION = '2.4.'

if not R6_pack.__version__.startswith(TARGET_VERSION):
    warnings.warn(
        'This was designed to match R6 version starting with %s '
        'but you have %s' % (TARGET_VERSION, R6_pack.__version__)
    )

R6_weakpack = WeakPackage(R6_pack._env,
                          R6_pack.__rname__,
                          translation=R6_pack._translation,
                          exported_names=R6_pack._exported_names,
                          on_conflict='warn',
                          version=R6_pack.__version__,
                          symbol_r2python=R6_pack._symbol_r2python,
                          symbol_resolve=R6_pack._symbol_resolve)

dollar = rpy2.robjects.baseenv['$']

# This will map an `rid` (identifier for an R object of class
# R6ClassGenerator) to a Python class inheriting from R6.
_CLASSMAP = dict()


def _static_classmap(clsgenerator: 'R6ClassGenerator') -> typing.Type['R6']:
    return _CLASSMAP.get(clsgenerator.rid, R6)


def dollar_getter(name: str) -> (
        typing.Callable[[rpy2.rinterface.SexpEnvironment], rpy2.rinterface.Sexp]
):
    """Convenience partial function for R's `$`.

    The R function `$` fetches attributes and is often
    found in R code. For example, `object$name` to
    get the attribute "name" of object "object".

    Args:
      name (str): the name of the R attribute to fetch
    Returns:
      The R object associated with the attribute.
    """
    def inner(obj):
        return dollar(obj, name)
    return inner


def _classname(obj):
    res = dollar(obj, 'classname')
    if res is not rpy2.robjects.NULL:
        assert len(res) == 1
        res = res[0]
    return res


def _build_attr_dict(clsgenerator: 'R6ClassGenerator') -> (
        typing.Dict[str, typing.Union[None, property]]
):
    res = dict()
    if clsgenerator.public_methods.names != rpy2.robjects.NULL:
        res.update((x, None) for x in clsgenerator.public_methods.names)
    if clsgenerator.public_fields.names != rpy2.robjects.NULL:
        res.update((x, property) for x in clsgenerator.public_fields.names)
    return res


def _build_docstring(clsgenerator: 'R6ClassGenerator') -> str:
    res = """Mapped R6 class "{classname}".

    The class is created dynamically from the R6 class definition
    in R.
    """.format(classname=_classname(clsgenerator))
    return textwrap.dedent(res)


def _r6__init__(self, *args, **kwargs):
    r6classgen = self.__R6CLASSGENERATOR__
    instance = dollar(r6classgen, r6classgen._FACTORY_NAME)(*args, **kwargs)
    self.__ROBJECT__ = instance


def r6_createcls(clsgenerator: 'R6ClassGenerator',
                 bases: typing.Tuple[typing.Type['R6']]) -> typing.Type['R6']:
    """Create a Python class matching R's R6ClassGenerator.

    Args:
      clsgenerator (R6ClassGenerator): an instance of class R6ClassGenerator

    Returns:
      A Python class
    """
    cls = R6Meta(
        _classname(clsgenerator),
        bases,
        {'__DEFAULT_ATTRS__': _build_attr_dict(clsgenerator),
         # TODO: Can we have a class-level __sexp__ and make it implement
         # the SupportSexp protocol ?
         '__R6CLASSGENERATOR__': clsgenerator,
         '__doc__': _build_docstring(clsgenerator),
         '__init__': _r6__init__}
    )
    return cls


def _dynamic_classmap(clsgenerator: 'R6ClassGenerator',
                      bases: typing.Optional[typing.Tuple[typing.Type]] = None) -> typing.Type:
    lineage = [clsgenerator]
    cur_clsgen = clsgenerator.inherit
    while cur_clsgen is not rpy2.rinterface.NULL:
        # cur_clsgen is a symbol for which we need to retrieve the mapped
        # object
        # TODO: may be there is an equivalent of `local()`, or of `eval()`
        # using an environment or frame, at the C API level ?
        cur_clsgen = rpy2.rinterface.baseenv['local'](
            cur_clsgen,
            dollar(lineage[-1], 'parent_env')
        )
        lineage.append(cur_clsgen)
        if cur_clsgen.rid in _CLASSMAP:
            break
        cur_clsgen = dollar(cur_clsgen, 'inherit')

    if bases is None:
        bases = (R6, )
    bases = list(bases)
    while lineage:
        cur_clsgen = lineage.pop()
        if not isinstance(cur_clsgen, R6ClassGenerator):
            cur_clsgen = type(clsgenerator)(cur_clsgen)
        bases.append(
            r6_createcls(
                cur_clsgen, tuple(reversed(bases))
            )
        )
        _CLASSMAP[cur_clsgen.rid] = bases[-1]
    return _CLASSMAP[clsgenerator.rid]


def _r6class_method_wrap(clsgenerator: 'R6ClassGenerator',
                         r6cls: typing.Type['R6'],
                         name: str = 'new') -> typing.Callable:
    """Wrapper for instance-specific static method."""
    def inner(*args, **kwargs):
        res = dollar(clsgenerator, name)(*args, **kwargs)
        return r6cls(res)
    return inner


class R6Meta(abc.ABCMeta):
    """Metaclass for R6 obbjects.

    This metaclass looks for an attribute __DEFAULT_ATTRS__ (a dict[str, None|property]).
    Each key in (a str) in that dict is the name of an attribute in the R6 object and
    automatically generates an attribute in the Python concrete class (unless the class
    definition already has an attribute with that name."""

    def __new__(meta, name, bases, attrs, **kwds):
        default_attrs = attrs.get('__DEFAULT_ATTRS__', None)
        if default_attrs is None:
            for b in bases:
                if hasattr(b, '__DEFAULT_ATTRS__'):
                    default_attrs = b.__DEFAULT_ATTRS__
                    break
        if default_attrs is None:
            raise ValueError(
                'Classes using the type {} must have an '
                'attribute __DEFAULT_ATTRS__'.format(str(meta))
            )
        attr_names = set(default_attrs)
        assert len(attr_names) == len(default_attrs)
        for key in (attr_names
                    .difference(attrs.keys())):
            wrapper = default_attrs[key]
            if wrapper:
                attrs[key] = wrapper(dollar_getter(key))
            else:
                attrs[key] = dollar_getter(key)
        cls = type.__new__(meta, name, bases, attrs, **kwds)
        return cls


def is_r6classgenerator(robj: rpy2.rinterface.Sexp) -> bool:
    """Determine if an R objects is an R6ClassGenerator."""
    return (
        robj.typeof == rpy2.rinterface.RTYPES.ENVSXP
        and
        tuple(robj.rclass) == ('R6ClassGenerator',)
    )


class R6ClassGenerator(rpy2.robjects.Environment,
                       metaclass=R6Meta):
    """Factory of constructors for R6 objects.

    Each instance of this class has a staticmethod new()
    (or an alternative name specified through factory_name) that is
    effectively a constructor and can be called to create a new
    instance of the corresponding R6 class.

    The resulting object is of type defined by the method __CLASSMAP__."""

    __DEFAULT_ATTRS__ = {
        'active': None,
        'class': property,
        'classname': property,
        'clone_method': None,
        'debug': None,
        'debug_names': property,
        'get_inherit': None,
        'has_private': property,
        'inherit': property,
        'is_locked': property,
        'lock': None,
        'lock_class': property,
        'lock_objects': property,
        # 'new' has a special treatment. see __init__.
        'parent_env': property,
        'portable': property,
        'private_fields': property,
        'private_methods': property,
        'public_fields': property,
        'public_methods': property,
        'self': property,
        'set': None,
        'undebug': None,
        'unlock': None
    }
    _FACTORY_NAME = 'new'

    def __init__(self, robj: rpy2.rinterface.SexpEnvironment):
        assert is_r6classgenerator(robj)
        super().__init__(o=robj)

        r6cls = self.__CLASSMAP__()
        self.__R6CLASS__ = r6cls
        if not hasattr(self, self._FACTORY_NAME):
            setattr(self, self._FACTORY_NAME, r6cls)


class R6StaticClassGenerator(R6ClassGenerator,
                             metaclass=R6Meta):

    __CLASSMAP__ = _static_classmap


class R6DynamicClassGenerator(R6ClassGenerator,
                              metaclass=R6Meta):

    __CLASSMAP__ = _dynamic_classmap


class R6(rpy2.rinterface.sexp.SupportsSEXP,
         metaclass=R6Meta):
    """Base R6 class.

    The underlying R object is an R environment at the base/C level.
    However, we do not want to inherit all methods from
    rpy2.robjects.Environment or even rpy2.rinterface.SexpEnvironment to
    allow for class definitions with class attributes (methods and properties)
    matching the R class definitions as closely as possible.
    """
    __DEFAULT_ATTRS__ = {}
    __ROBJECT__ = None

    def __repr__(self):
        return '{} at {}'.format(repr(type(self)), hex(id(self)))

    @property
    def __sexp__(self) -> _rinterface.SexpCapsule:
        return self.__ROBJECT__.__sexp__

    @__sexp__.setter
    def __sexp__(self, value: _rinterface.SexpCapsule):
        self.__ROBJECT__.__sexp__ = value

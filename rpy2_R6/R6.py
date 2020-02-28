import rpy2.rinterface
import rpy2.robjects
from rpy2.robjects.packages import (importr,
                                    WeakPackage)
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
                          on_conflict="warn",
                          version=R6_pack.__version__,
                          symbol_r2python=R6_pack._symbol_r2python,
                          symbol_resolve=R6_pack._symbol_resolve)

dollar = rpy2.robjects.baseenv['$']

_CLASSMAP = dict()


def _default_classmap(clsgenerator):
    return _CLASSMAP.get(clsgenerator.classname, R6)


def dollar_getter(name: str) -> (
        typing.Callable[[rpy2.rinterface.SexpEnvironment], rpy2.rinterface.Sexp]
):
    """Convenience partial function for the R `$`.

    The R function `$` fetches attributes and is often
    found in R code under the form `object$name`.

    Args:
      name (str): the name of the R attribute to fetch
    Returns:
      The R object associated with the attribute.
    """
    def inner(obj):
        return dollar(obj, name)
    return inner


def _build_attr_dict(clsgenerator: 'R6ClassGenerator') -> (
        typing.Dict[str, typing.Union[None, property]]
):
    res = dict()
    if clsgenerator.public_methods.names != rpy2.robjects.NULL:
        res.update((x, None) for x in clsgenerator.public_methods.names)
    if clsgenerator.public_fields.names != rpy2.robjects.NULL:
        res.update((x, property) for x in clsgenerator.public_fields.names)
    return res


def r6_createcls(clsgenerator: 'R6ClassGenerator') -> 'typing.Type[R6]':
    """Create a Python class matching R's R6ClassGenerator.

    Args:
      clsgenerator (R6ClassGenerator): an instance of class R6ClassGenerator

    Returns:
      A Python class
    """
    cls = R6Meta(
        clsgenerator.classname,
        (R6, ),
        {'__DEFAULT_ATTRS__': _build_attr_dict(clsgenerator)}
    )
    return cls


def _dynamic_classmap(clsgenerator):
    classname = clsgenerator.classname
    if classname not in _CLASSMAP:
        _CLASSMAP[classname] = r6_createcls(clsgenerator)
    return _CLASSMAP[classname]


def _r6class_new(clsgenerator, r6cls):
    """Wrapper for instance-specific static method."""
    def inner(*args, **kwargs):
        res = dollar(clsgenerator, 'new')(*args, **kwargs)
        return r6cls(res)
    return inner


class R6Meta(type):

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


class R6ClassGenerator(rpy2.robjects.Environment,
                       metaclass=R6Meta):
    """Factory of constructors for R6 objects."""

    __DEFAULT_ATTRS__ = {
        'active': None,
        'class': property,
        'classname': property,
        'clone_method': None,
        'debug': None,
        'debug_names': property,
        'get_inherit': None,
        'has_private': property,
        'inherit': None,
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

    __CLASSMAP__ = _default_classmap

    def __init__(self, robj: rpy2.rinterface.SexpEnvironment):
        # TODO: check that robj is genuinely an R R6ClassGenerator
        super().__init__(o=robj)

        r6cls = self.__CLASSMAP__(self)
        if not hasattr(self, 'new'):
            self.new = _r6class_new(self, r6cls)

        self._classname = None

    @property
    def classname(self):
        if not self._classname:
            classname = dollar(self, 'classname')
            if classname is rpy2.robjects.NULL:
                self._classname = rpy2.robjects.NULL
            else:
                assert len(classname) == 1
                self._classname = classname[0]
        return self._classname


class R6(rpy2.robjects.Environment,
         metaclass=R6Meta):

    __DEFAULT_ATTRS__ = {}

    def __repr__(self):
        return '{} at {}'.format(repr(type(self)), hex(id(self)))

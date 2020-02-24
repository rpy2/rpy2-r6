import rpy2.rinterface
import rpy2.robjects
from rpy2.robjects.packages import (importr,
                                    WeakPackage)
import warnings
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    R6_pack = importr('R6', on_conflict="warn")

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


def dollar_getter(name: str) -> rpy2.rinterface.Sexp:
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


def r6_createcls(clsgenerator: 'R6ClassGenerator'):
    """Create a Python class matching R's R6ClassGenerator.

    Args:
      clsgenerator (R6ClassGenerator): an instance of class R6ClassGenerator

    Returns:
      A Python class
    """
    cls = R6Meta(
        clsgenerator.classname,
        (R6, ),
        {'__PUBLIC_ATTRS__': set(clsgenerator.public_methods.names)}
    )
    return cls


def _r6class_new(self):
    """Wrapper for instance-specific static method."""
    def inner(*args, **kwargs):
        res = dollar(self, 'new')(*args, **kwargs)
        cls = _CLASSMAP.get(self.classname, R6)
        return cls(res)
    return inner


class R6Meta(type):
    
    def __new__(meta, name, bases, attrs, **kwds):
        assert '__PUBLIC_ATTRS__' in attrs
        for default_attr in (attrs['__PUBLIC_ATTRS__']
                             .difference(attrs.keys())):
            attrs[default_attr] = property(dollar_getter(default_attr))
        cls = type.__new__(meta, name, bases, attrs, **kwds)
        return cls


class R6ClassGenerator(rpy2.robjects.Environment,
                       metaclass=R6Meta):

    __PUBLIC_ATTRS__ = {
        'active',
        'class',
        'classname',
        'clone_method',
        'debug',
        'debug_names',
        'get_inherit',
        'has_private',
        'inherit',
        'is_locked',
        'lock',
        'lock_class',
        'lock_objects',
        # 'new' has a special treatment. see __init__().
        'parent_env',
        'portable',
        'private_fields',
        'private_methods',
        'public_fields',
        'public_methods',
        'self',
        'set',
        'undebug',
        'unlock'
    }

    def __init__(self, robj):
        # TODO: check that robj is genuinely an R R6ClassGenerator
        super().__init__(o=robj)
        
        if not hasattr(self, 'new'):
            self.new = _r6class_new(self)

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

    __PUBLIC_ATTRS__ = set()

    def __repr__(self):
        return '{} at {}'.format(repr(type(self)), hex(id(self)))

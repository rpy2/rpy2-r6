import types
import weakref

import rpy2.rinterface_lib as rinterface_lib
import rpy2.rinterface_lib._rinterface_capi as _rinterface_capi
import rpy2.robjects as robjects
import rpy2_r6.utils


class R6Object(_rinterface_capi.SupportsSEXP):
    """Base class for R6 objects."""

    __CACHE = weakref.WeakValueDictionary()
    __PRIVATE_ATTRS__ = set()

    __slots__ = ('_robj', )

    @classmethod
    def from_robj(cls, robj: _rinterface_capi.SupportsSEXP):
        assert isinstance(robj, _rinterface_capi.SupportsSEXP)
        if id(robj) not in cls.__CACHE:
            clsinstance = cls(robj)
            cls.__CACHE[id(robj)] = clsinstance
        return cls.__CACHE[id(robj)]()

    def __init__(self, robj):
        if robj is robjects.NULL:
            raise ValueError
        self._robj = robj

    def __dir__(self):
        keys = set(self._robj.keys())

        private = self.__PRIVATE_ATTRS__.intersection(keys)
        public = keys.difference(self.__PRIVATE_ATTRS__)

        return (
            list(public) +
            [
                f'_{key}' for key in private
            ]
        )

    def __getattr__(self, attr):
        if attr.startswith('_') and attr[1:] in self.__PRIVATE_ATTRS__:
            value = self._robj[attr[1:]]
        elif not attr.startswith('_') and attr not in self.__PRIVATE_ATTRS__:
            value = self._robj[attr]
        else:
            raise AttributeError(attr)

        if (
                isinstance(value, rinterface_lib.sexp.Sexp)
                and
                set(value.rclass) == {'function'}
        ):
            return types.MethodType(
                robjects.functions.wrap_r_function(value, name=attr, is_method=True),
                self
            )
        return value

    def __eq__(self, other):
        if isinstance(other, R6Object):
            return self._robj is other._robj
        return NotImplemented

    @property
    def __sexp__(self):
        return self._robj.__sexp__

    @__sexp__.setter
    def __sexp__(self, value):
        self._robj.__sexp__ = value


class R6Class(R6Object):
    """Mapping for R6::ClassFactoryGenerator() in R."""

    __PRIVATE_ATTRS__ = set(rpy2_r6.utils.__DEFAULT_GENERATOR_ATTRS__.keys())

    __slots__ = ()

    @property
    def class_name(self):
        return self._robj["classname"][0]

    def __call__(self, *args, **kwargs):
        return R6Instance(self._robj['new'](*args, **kwargs))

    def __repr__(self):
        return f'R6Class<{self.class_name}>'

    def __getattr__(self, attr):
        if (
                'public_fields' in self._robj
                and
                self._robj['public_fields'] is not robjects.NULL
                and
                attr in self._robj['public_fields']
        ):
            return self._robj['public_fields'][attr]
        return super().__getattr__(attr)

    def __rmro__(self):
        mro = []
        rcls = self._robj
        while True:
            mro.append(rcls['classname'][0])
            if 'inherit' in rcls and rcls['inherit']:
                rcls = robjects.r(f"get('{rcls['inherit']}')")
            else:
                break
        return mro


class R6Instance(R6Object):

    __PRIVATE_ATTRS__ = {
        'clone',
        'initialize'
    }

    __slots__ = ()

    @property
    def class_name(self):
        return self._robj.rclass[0]

    def __repr__(self):
        return f'R6Instance<{self.class_name}>'

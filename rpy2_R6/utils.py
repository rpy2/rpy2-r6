import enum
import rpy2.robjects


class ATTR_TYPE(enum.Enum):
    PROPERTY = 1
    METHOD = 2
    FACTORYMETHOD = 3


# Default attributes for class generators in R6.
__DEFAULT_GENERATOR_ATTRS__ = {
    'active': ATTR_TYPE.METHOD,
    'class': ATTR_TYPE.PROPERTY,
    'classname': ATTR_TYPE.PROPERTY,
    'clone_method': ATTR_TYPE.METHOD,
    'debug': ATTR_TYPE.METHOD,
    'debug_names': ATTR_TYPE.PROPERTY,
    'get_inherit': ATTR_TYPE.METHOD,
    'has_private': ATTR_TYPE.PROPERTY,
    'inherit': ATTR_TYPE.PROPERTY,
    'is_locked': ATTR_TYPE.PROPERTY,
    'lock': ATTR_TYPE.METHOD,
    'lock_class': ATTR_TYPE.PROPERTY,
    'lock_objects': ATTR_TYPE.PROPERTY,
    'new': ATTR_TYPE.FACTORYMETHOD,
    'parent_env': ATTR_TYPE.PROPERTY,
    'portable': ATTR_TYPE.PROPERTY,
    'private_fields': ATTR_TYPE.PROPERTY,
    'private_methods': ATTR_TYPE.PROPERTY,
    'public_fields': ATTR_TYPE.PROPERTY,
    'public_methods': ATTR_TYPE.PROPERTY,
    'self': ATTR_TYPE.PROPERTY,
    'set': ATTR_TYPE.METHOD,
    'undebug': ATTR_TYPE.METHOD,
    'unlock': ATTR_TYPE.METHOD
}

dollar = rpy2.robjects.baseenv['$']

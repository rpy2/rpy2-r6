import rpy2.robjects
import rpy2.robjects.methods
from rpy2.robjects import vectors
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


class R6(rpy2.robjects.Environment):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

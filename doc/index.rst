R's R6 classes in rpy2/Python
=============================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Introduction
------------

[R6](https://r6.r-lib.org/) is one of the OOP systems available
to R programmers, and is relatively similar to other OOP systems
non-R programmers might be familiar with. In the R6 authors'
own words "this style of programming is also sometimes referred
to as classical object-oriented programming".

This Python package is using :mod:`rpy2` to provide Pythonic
wrappers for R6 classes and instances, and make the integration
of R6-based class models into Python code as natural and as
readable as possible.


A first example
---------------

To demonstrate how it is working, we use the R package
`scales` (a dependency of `ggplot2`).

.. code-block:: python

   import rpy2_R6.R6 as r6
   import rpy2.rinterface
   import rpy2.robjects
   from rpy2.robjects.packages import importr
   scales = importr('scales')

In R's R6, a class definition is an instance of class
`ClassFactoryGenerator`, and its method `new()` is
is used to create instances of class `R6`. In a way,
the class `ClassFactorGenerator` is in fact closer to a
metaclass, and its instances are like constructors
for instance of the class of interest.

This is relatively different from the way Python classes
are defined and are working so we tried to have a wrapper
that is both faithful to the R code, since this can make
debugging or using the R documentation easier, while also
allowing a rather Pythonic feel.

To start, we start with `Range`, an instance of class
`ClassFactoryGenerator` in the package `scales`, and we wrap
it to be an instance of our matching Python class.

.. code-block:: python

   range_factory = r6.R6DynamicClassGenerator(scales.Range)

.. note::

   The automatic wrapping can be done through rpy2's conversion
   system. It is planned to offer the option is in this package.


In R, creating a new instance of `Range` would be done with:

.. code-block:: r

   library(scales)
   obj <- Range$new()

That instance `obj` is of R class `("Range", "R6")`, meaning
an instance of class "Range", inheriting from class "R6" (on the
R side).

.. code-block:: rconsole

   >>> class(Range$new())
   c("Range", "R6")

We are able to write essentially the same code in Python:

.. code-block:: python

   obj = range_factory.new()

The type of the resulting object is a Python class `Range`:

.. code-block:: python

   >>> type(obj)
   rpy2_R6.R6.Range


Dynamic class generation
------------------------

We never explicitly defined that class `Range`. It
was dynamically created by our package
to reflect the R class definition from
the `ClassFactoryGenerator` instance.

The use of a constructor method `new` is not the
most common way to instanciate objects in python though,
so we made our method `new` something a little unconventional:
it is a nested class.
This leads to a much more familiar way to create
instances of class `Range`:

.. code-block:: python

   Range = range_factory.new
   myrange = Range()

The lineage (inheritance tree) for the Python class `Range` is
dynamically generated to match the one for the R R6 class
definition.

.. code-block:: python

   >>> import inspect
   >>> inspect.getmro(Range)
   (rpy2_R6.R6.Range,
    rpy2_R6.R6.R6,
    rpy2.rinterface_lib.sexp.SupportsSEXP,
    object)

An other example with a longer lineage:
    
.. code-block:: python

   >>> DiscreteRange = r6.R6DynamicClassGenerator(scales.DiscreteRange).new
   >>> inspect.getmro(DiscreteRange)
   (rpy2_R6.R6.DiscreteRange,
    rpy2_R6.R6.Range,
    rpy2_R6.R6.R6,
    rpy2.rinterface_lib.sexp.SupportsSEXP,
    object)


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

R's R6 classes in rpy2/Python
=============================

Repository: https://github.com/rpy2/rpy2-R6

.. contents:: Table of Contents


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

OOP in R's R6 is relatively different from the way Python classes
are defined and are working.
In R6 a class definition is an instance of class
`ClassFactoryGenerator`, that has at one method (`new()`) acting
as a factory that can create instances inheriting from class `R6`.
One can see this a some form of metaprogramming, with instances class
`ClassFactorGenerator` acting like metaclasses by defining the
corresponding child classes dynamically.

Despite the challenge, we are trying to have a wrapper
that is both faithful to the R code, since this can make
debugging or using the R documentation easier, while also
allowing a rather Pythonic feel. Currently there are two alternative wrappers:
:mod:`rpy2_r6.r6a` and :mod:`rpy2_r6.r6b`.


A first example
---------------

To demonstrate how it is working, we use the R package
`scales` (a dependency of `ggplot2`).

.. doctest:: first_example

   import rpy2.rinterface
   import rpy2.robjects
   from rpy2.robjects.packages import importr
   scales = importr('scales')   

In this short tutorial we start with `Range`, an instance of class
`ClassFactoryGenerator` in the package `scales`, and we wrap
it to be an instance of our matching Python class.

In R, creating a new instance of `Range` would be done with:

.. code-block:: r

   library(scales)
   obj <- Range$new()

That instance `obj` is of R class `("Range", "R6")`, meaning that
this is an instance of class "Range" inheriting from class "R6" (on the
R side).

.. code-block:: rconsole

   > class(Range$new())
   c("Range", "R6")


r6a
---

The wrapper was kindly contributed in a PR for rpy2 by Matthew Wardrop (@matthewwardrop),
and was only slightly adapted to use the recent `SupportsSEXP` interface in rpy2.

In this approach the class `ClassFactoryGenerator` in R is mapped to :class:`rpy2_r6.r6a.R6Class`.

.. testcode:: first_example

   range_factory_r6a = r6a.R6Class(scales.Range)


.. testcode:: first_example

   range_r6a = range_factory_r6a.new()

The instance is a generic :class:`rpy2_r6.r6a.R6` in Python, with the R class name available
through a property of that object:

.. doctest::

   >>> type(range_r6a)
   rpy2_r6.r6a.R6
   >>> range_r6b.class_name
   'Scale'

The properties and methods available for the object in R are dynamically resolved from the Python side,
and private attributes in the R6 definitions have an underscore prefixed to their attribute name in Python.
For example, the private method R6 `clone` for the object is accessed with `_clone` in Python: 

.. testcode:: first_example

   range_r6a._clone()


r6b
---

.. testcode:: first_example

   range_factory_r6b = r6b.R6DynamicClassGenerator(scales.Range)

.. note::

   Automatic wrapping could be achieved through rpy2's own conversion
   system. It is planned to offer the option to facilitate this in this package.


We are able to write essentially the same code in Python:

.. testcode:: first_example

   range_r6b = range_factory_r6b.new()

The type of the resulting object is a Python class `Range`:

.. doctest::

   >>> type(range_r6b)
   rpy2_r6.r6b.Range


Dynamic class generation
^^^^^^^^^^^^^^^^^^^^^^^^

You'll note that we never explicitly defined the class `Range`; it
was dynamically created by our package
to reflect the R class definition from
the `ClassFactoryGenerator` instance.

The method `new` is a factory:

.. testcode:: first_example

   myrange = range_factory_r6b.new

The underlying class is:

.. testcode:: first_example

   Range = range_factory_r6b.__R6CLASS__
   
The lineage (inheritance tree) for the Python class `Range` is
dynamically generated to match the one for the R6 class
definition in R.

.. doctest:: first_example

   >>> import inspect
   >>> inspect.getmro(Range)
   (rpy2_r6.r6b.Range,
    rpy2_r6.r6b.R6,
    rpy2.rinterface_lib.sexp.SupportsSEXP,
    object)

An other example with a longer lineage:
    
.. doctest:: first_example

   >>> DiscreteRange = r6b.R6DynamicClassGenerator(scales.DiscreteRange).new
   >>> inspect.getmro(DiscreteRange)
   (rpy2_r6.r6b.DiscreteRange,
    rpy2_r6.r6b.Range,
    rpy2_r6.r6b.R6,
    rpy2.rinterface_lib.sexp.SupportsSEXP,
    object)


Indices and tables
==================

* :ref:`genindex`
* :ref:`search`

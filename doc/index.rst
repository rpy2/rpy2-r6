R's R6 classes in rpy2/Python
=============================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

R6 is one of the OOP systems available to R programmers,
and is relatively similar to other OOP systems non-R
programmers might be familiar with.

This package is using :mod:`rpy2` to provide Pythonic
wrappers for R6 classes and instances.

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
is used to create instances of class `R6`.
This is relatively different from the way Python classes
are working so we tried to get closer to Python class definitions.

We start with `Range`, an instance of class `ClassFactoryGenerator`
in the package `scales`, and we wrap it to be an instance
of our matching Python class.

.. code-block:: python

   range_factory = r6.R6DynamicClassGenerator(scales.Range)

In R, creating a new instance of "Range" would be done with:

.. code-block:: r

   obj <- Range$new()

That instance `obj` could be og class `("Range", "R6")`, meaning
an instance of class "Range", inheriting from class "R6".

Our wrapper can function similarly:

.. code-block:: python

   obj = range_factory.new()
   
   # The python objects is of a class lineage matching.
   type(obj)  # result: rpy2_R6.R6.Rnage
   type(obj).__base__  # result: rpy2_R6.R6.R6

This is achieved by optionally dynamically creating
Python classes mapping the R6 classes.

However, the use of a constructor method `new` is not the
most common way to instanciate objects in python. So,
we made our method new something a little unconventional:
it is a nested class that was dynamically generated from
the class description in the R `ClassFactoryGenerator`
instance. This is a much more familiar way to create
instances of class `Range`:

.. code-block:: python

   Range = range_factory.new
   myrange = Range()

   # or

   Range = type(obj)
   myrange = Range()


The lineage (inheritance tree) for the Python class `Range` is
dynamically generated to match the R6 one, up until the class R6.

.. code-block:: python

   >>> import inspect
   >>> inspect.getmro(Range)
   (rpy2_R6.R6.Range,
    rpy2_R6.R6.R6,
    rpy2.rinterface_lib.sexp.SupportsSEXP,
    object)


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

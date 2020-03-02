# rpy2-R6
![Python package](https://github.com/rpy2/rpy2-R6/workflows/Python%20package/badge.svg)

`rpy2` extension package to faciliate handling of R6 objects


```python
import rpy2_R6.R6 as r6
import rpy2.rinterface
import rpy2.robjects

# Run R's own code examples for R6 class
rpy2.robjects.r('example(R6Class)')

# Fetch the class definition (in R6, an instance of
# class ClassFactoryGenerator) 'Queue' resulting from
# running the code examples
_Queue = rpy2.robjects.r('Queue')

# Map that R object to a Python object, that is
# effectively a factory of objects of that class.
queue_factory = r6.R6DynamicClassGenerator(_Queue)

# In R, creating a new object would be done with.
#   obj <- Queue$new()
# The class for obj is ("Queue", "R6"), meaning
# an instance of class "Queue", inheriting from class "R6".

obj = queue_factory.new()

# The python objects is of a class lineage matching.
type(obj)  # result: rpy2_R6.R6.Queue
type(obj).__base__  # result: rpy2_R6.R6.R6

# This is achieved by optionally dynamically creating
# Python classes mapping the R6 classes.

# The use of the constructor method "new" is not the
# most common way to instanciate objects in python,
# but it also possible to call the class object.

Queue = QueueClass.new
myqueue = Queue()

# or

Queue = type(obj)
myqueue = Queue()
```
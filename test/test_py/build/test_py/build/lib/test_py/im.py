import inspect

class A():
  def __init__(self):
    b = B()

class B:
  def __init__(self):
    print("B.b()")
    stack = inspect.stack()
    print(stack[1][0].f_code.co_name)
    print(stack[1][0].f_locals["self"].__class__.__name__)
    # the_class = stack[1][0].f_locals["self"].__class__.__name__
    # the_method = stack[1][0].f_code.co_name
    # print("  I was called by {}.{}()".format(the_class, the_method))

a = A()
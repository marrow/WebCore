# encoding: utf-8

"""

"""


__all__ = []



def pre_post_wrapper(pre=None, post=None, lock=None):
    """
    Decorates a method excecuting pre and post methods around it.

    Can be used to decorate the same method in different subclasses and takes
    care that pre is executed only once at the first cooperative call and post
    once at the end of the cooperative call-chain.

        >>> entries = 0
        >>> exits = 0
        >>> def pre(*args, **kw): global entries; entries += 1
        >>> def post(*args, **kw): global exits; exits += 1
        >>> class A(object):
        ...     @pre_post_wrapper(pre, post)
        ...     def say_name(self, name):
        ...         print name
        >>> class B(A):
        ...     @pre_post_wrapper(pre, post)
        ...     def say_name(self, name):
        ...         super(B, self).say_name(name)
        ...         print name
        >>> class C(B):
        ...     @pre_post_wrapper(pre, post)
        ...     def say_name(self, name):
        ...         super(C, self).say_name(name)
        ...         print name
        >>> c = C()
        >>> c.say_name('foo')
        foo
        foo
        foo
        >>> entries
        1
        >>> exits
        1

    A reentrant lock can be passed to syncronize the wrapped method. It is a
    must if the instance is shared among several threads.
    """
    def wrapped(func, self, *args, **kw):
        counter_name = '__%s_wrapper_counter' % func.func_name
        if lock:
            lock.aquire()
        try:
            counter = getattr(self, counter_name, 0) + 1
            setattr(self, counter_name, counter)
            if counter == 1 and pre:
                pre(self, *args, **kw)
            output = func(self, *args, **kw)
            counter = getattr(self, counter_name)
            setattr(self, counter_name, counter - 1)
            if counter == 1:
                delattr(self, counter_name)
                if post: post(self, *args, **kw)
        finally:
            if lock:
                lock.release()
        return output
    return decorator(wrapped)

def pre_post_hooks(pre_name=None, post_name=None, lock=None):
    def wrapped(func, self, *args, **kw):
        counter_name = '__%s_wrapper_counter' % func.func_name
        bases = list(inspect.getmro(self.__class__))
        if lock:
            lock.aquire()
        try:
            counter = getattr(self, counter_name, 0) + 1
            setattr(self, counter_name, counter)
            if counter == 1 and pre_name:
                for base in bases:
                    try:
                        # make sure we use the hook  defined in base
                        base.__dict__[pre_name](self, *args, **kw)
                    except KeyError:
                        pass
            output = func(self, *args, **kw)
            counter = getattr(self, counter_name)
            setattr(self, counter_name, counter - 1)
            if counter == 1:
                delattr(self, counter_name)
                if post_name:
                    for base in bases:
                        try:
                            base.__dict__[post_name](self, *args, **kw)
                        except KeyError:
                            pass
        finally:
            if lock:
                lock.release()
        return output
    return decorator(wrapped)
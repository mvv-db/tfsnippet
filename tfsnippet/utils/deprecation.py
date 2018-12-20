import warnings

import six

__all__ = ['deprecated']


def _deprecated_warn(message):
    warnings.warn(message, category=DeprecationWarning)


def _name_of(target):
    return target.__name__


class deprecated(object):
    """
    Decorate a class, a method or a function to be deprecated.

    Usage::

        @deprecated()
        def some_function():
            ...

        @deprecated()
        class SomeClass:
            ...
    """

    def __init__(self, message='', version=None):
        """
        Construct a new :class:`deprecated` object, which can be
        used to decorate a class, a method or a function.

        Args:
            message: The deprecation message to display.  It will be appended
                to the end of auto-generated message, i.e., the final message
                would be "`<name>` is deprecated; " + message.
            version: The version since which the decorated target is deprecated.
        """
        self._message = message
        self._version = version

    def __call__(self, target):
        if isinstance(target, six.class_types):
            return self._deprecate_class(target)
        else:
            return self._deprecate_func(target)

    def _deprecate_class(self, cls):
        msg = 'Class `{}` is deprecated'.format(_name_of(cls))
        if self._message:
            msg += '; {}'.format(self._message)
        else:
            msg += '.'

        # patch the __init__ of the class
        init = cls.__init__

        @six.wraps(init)
        def wrapped(*args, **kwargs):
            _deprecated_warn(msg)
            return init(*args, **kwargs)

        cls.__init__ = wrapped
        cls.__doc__ = self._update_doc(cls.__doc__)

        return cls

    def _deprecate_func(self, func):
        msg = 'Function or method `{}` is deprecated'.format(_name_of(func))
        if self._message:
            msg += '; {}'.format(self._message)
        else:
            msg += '.'

        @six.wraps(func)
        def wrapped(*args, **kwargs):
            _deprecated_warn(msg)
            return func(*args, **kwargs)

        wrapped.__doc__ = self._update_doc(wrapped.__doc__)
        # Add a reference to the wrapped function so that we can introspect
        # on function arguments in Python 2 (already works in Python 3)
        wrapped.__wrapped__ = func

        return wrapped

    def _update_doc(self, doc):
        ret = '.. deprecated::'
        if self._version:
            ret += ' {}'.format(self._version)
        if self._message:
            ret += '\n  {}'.format(self._message)
        if doc:
            ret = '{}\n\n{}\n'.format(doc, ret)
        else:
            # The empty line before ".. deprecated" is required by sphinx
            # to correctly parse this deprecation block.
            ret = '\n{}\n'.format(ret)
        return ret

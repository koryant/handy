from __future__ import division, print_function, absolute_import
import numpy as np
from collections import Mapping, Iterable
from functools import wraps
from math import log10, floor

__all__ = ['amap', 'unpack_args', 'catch_exception', 'siground', 'DictToClass', 'DefaultDictToClass']


def amap(func, *args):
    '''array version of build-in map
    amap(function, sequence[, sequence, ...]) -> array
    Examples
    --------
    >>> amap(lambda x: x**2, 1)
    array(1)
    >>> amap(lambda x: x**2, [1, 2])
    array([1, 4])
    >>> amap(lambda x,y: y**2 + x**2, 1, [1, 2])
    array([2, 5])
    >>> amap(lambda x: (x, x), 1)
    array([1, 1])
    >>> amap(lambda x,y: [x**2, y**2], [1,2], [3,4])
    array([[1, 9], [4, 16]])
    '''
    args = np.broadcast(None, *args)
    res = np.array([func(*arg[1:]) for arg in args])
    shape = args.shape + res.shape[1:]
    return res.reshape(shape)


def unpack_args(func):
    @wraps(func)
    def wrapper(args):
        if isinstance(args, Mapping):
            return func(**args)
        elif isinstance(args, Iterable):
            return func(*args)
        else:
            return func(args)
    return wrapper


def catch_exception(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            raise
        except Exception as msg:
            print('failed:  %s(*%s, **%s)\nmessage: %s' %
                  (func.__name__, args, kwargs, msg))
    return wrapper


def siground(x, n):
    x, n = float(x), int(n)
    assert n > 0
    if x == 0:
        return ("%%.%if" % (n - 1)) % x
    m = 10 ** floor(log10(abs(x)))
    x = round(x / m, n - 1) * m
    p = floor(log10(abs(x)))
    if -3 < p < n:
        return ("%%.%if" % (n - 1 - p)) % x
    else:
        return ("%%.%ife%%+i" % (n - 1)) % (x / 10**p, p)


class DictToClass(object):
    def __init__(self, *args, **kwds):
        self.__dict__ = dict(*args, **kwds)


class DefaultDictToClass(object):
    def __init__(self, default_factory, *args, **kwds):
        from collections import defaultdict
        self.__dict__ = defaultdict(default_factory, *args, **kwds)

    def __getattr__(self, key):
        return self.__dict__[key]


def is_scalar(x):
    """
    >>> np.isscalar(np.array(1))
    False
    >>> is_scalar(np.array(1))
    True
    """
    if np.isscalar(x):
        return True
    elif isinstance(x, np.ndarray):
        return not x.ndim
    else:
        return False
        # return hasattr(x, "__len__")

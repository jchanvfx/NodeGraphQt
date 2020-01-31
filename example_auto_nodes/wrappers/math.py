from math import *

_pi = pi
_e = e
_tau = tau
_inf = inf
_nan = nan


# add contants as functions

def pi():
    print('pi', _pi)
    return _pi


def e():
    print('e', _e)
    return _e


def tau():
    print('tau', _tau)
    return _tau


def inf():
    print('inf', _inf)
    return _inf


def nan():
    print('nan', _nan)
    return _nan


# add basic math functions to math library

def add(x, y):
    return x + y


def sub(x, y):
    return x - y


def mul(x, y):
    return x * y


def div(x, y):
    return x / y

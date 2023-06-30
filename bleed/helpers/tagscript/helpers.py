from .classes import Converter


def converter(func):
    return Converter(func)

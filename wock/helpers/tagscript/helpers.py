from .classes import Converter


def converter(func):
    """
    Decorator to convert a function
    into a converter.
    """
    return Converter(func)

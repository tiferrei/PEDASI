from django.template import Library

register = Library()


@register.filter
def access(value, arg):
    """
    Template filter to access a dictionary by a key.

    :param value: Dictionary to access
    :param arg: Key to look up
    :return: Value of key in dictionary
    """
    return value[arg]

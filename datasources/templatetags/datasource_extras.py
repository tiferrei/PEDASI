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
    try:
        return value[arg]

    except KeyError:
        return None

    except TypeError:
        # Is a GroupedResult not a dictionary
        for item in value:
            if item.field.short_name == arg:
                return item

        return None

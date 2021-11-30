from django import template

register = template.Library()


@register.filter(name='get_dict_value')
def dict_val(dic, key):
    """
    Returns a numerical loop with the built in python range function

    """
    result = dic.get(key, 0.0)
    return result
"""
Custom template tags for timetable module.
"""
from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """
    Get an item from a dictionary using a key.
    Usage: {{ dict|get_item:key }}
    """
    if dictionary is None:
        return None
    return dictionary.get(str(key))

@register.filter
def get_attr(obj, attr_name):
    """
    Get an attribute from an object.
    Usage: {{ obj|get_attr:"attribute_name" }}
    """
    if obj is None:
        return None
    if isinstance(obj, dict):
        return obj.get(attr_name)
    return getattr(obj, attr_name, None)

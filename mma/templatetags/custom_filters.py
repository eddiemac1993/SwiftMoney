from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, "#FFFFFF")  # Default color if key not found

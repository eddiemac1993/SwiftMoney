from django import template

register = template.Library()

@register.filter
def in_list(value, arg):
    return value in arg.split(',')

from django import template
from num2words import num2words  # You may need to install num2words library

register = template.Library()

@register.filter
def number_to_words(value):
    try:
        return num2words(value, lang='en')
    except Exception:
        return ''

from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    # Check if the dictionary is None
    if dictionary is None:
        return None

    # Check if the key exists in the dictionary
    if key in dictionary:
        return dictionary[key]
    else:
        return None

@register.filter(name='add_class')
def add_class(field, css_class):
    return field.as_widget(attrs={"class": css_class})

@register.filter
def divide_by(value, arg):
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError):
        return None

@register.filter
def contains(value, arg):
    return str(arg) in value
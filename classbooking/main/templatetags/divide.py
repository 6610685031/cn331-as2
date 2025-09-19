from django import template

register = template.Library()


@register.filter
def divide(value, arg):
    try:
        return (float(value) / float(arg)) * 100
    except (ValueError, ZeroDivisionError):
        return None  # Handle errors gracefully

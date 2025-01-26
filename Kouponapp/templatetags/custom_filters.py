from django import template

register = template.Library()

@register.filter
def sub(value, arg):

    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def to_thai_year(value, format_string="d M Y H:i"):
    if value:
        # Convert to Thai Buddhist year by adding 543 to the year
        return value.strftime(format_string).replace(
            str(value.year), str(value.year + 543)
        )
    return value
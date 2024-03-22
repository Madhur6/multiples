from django import template
import os
import re

register = template.Library()

@register.filter
def filename(value):
    match = re.search(r'IMG_\d{1,3}_(.+)', value)
    if match:
        return match.group(1)
    return value # Return the original value if no match is found 
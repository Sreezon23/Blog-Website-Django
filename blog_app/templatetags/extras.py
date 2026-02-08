from django import template
import re, math
register = template.Library()

@register.filter
def reading_time(html):
    text = re.sub('<[^<]+?>', '', html or '')
    words = max(1, len(text.split()))
    return f"{math.ceil(words/200)} min read"

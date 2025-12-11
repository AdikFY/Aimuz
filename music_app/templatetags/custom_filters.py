from django import template

register = template.Library()

@register.filter
def duration_format(value):
    if value is None:
        return "0:00"
    minutes = int(value) // 60
    seconds = int(value) % 60
    return f"{minutes}:{str(seconds).zfill(2)}"

@register.filter(name='add_class')
def add_class(field, css_class):
    return field.as_widget(attrs={"class": css_class})

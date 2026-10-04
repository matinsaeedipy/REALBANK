from django import template

from bank.i18n import tr

register = template.Library()


@register.simple_tag
def t(key, **kwargs):
    return tr(key, **kwargs)

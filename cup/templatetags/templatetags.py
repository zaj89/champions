from django import template

register = template.Library()


@register.filter
def in_group(players, group):
    return players.filter(group=group)

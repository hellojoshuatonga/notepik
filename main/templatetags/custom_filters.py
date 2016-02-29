from datetime import datetime, timedelta

from django import template
from django.utils import timezone
from django.utils.timesince import timesince

register = template.Library()

@register.filter
def timeago(value):
    """ 
    Filter to make datetime readable.
    e.g "5 mins ago, now, 5 days ago, etc"
    """

    # need to be aware in timezone : http://stackoverflow.com/questions/796008/cant-subtract-offset-naive-and-offset-aware-datetimes
    now = timezone.now()
    
    difference = now - value

    # try:
        # difference = now - value
    # except:
        # return value

    # if it's just a minute apart then return time like this -> '5 mins now'
    if difference <= timedelta(minutes=1):
        return 'just now'

    return '%(time)s ago' % {'time': timesince(value).split(', ')[0]}

@register.filter
def dict_get_item(dictionary, key):
    """ 
    Get a value out of a dictionary to use in templates
    """
    return dictionary.get(key)

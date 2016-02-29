# Python
import string
import random
import math
import datetime

# Django
from django.utils.timezone import utc



def get_expiration_date(hours=1):
    return datetime.datetime.now(tz=utc) + datetime.timedelta(hours=hours)

def random_str(size=5, chars=string.ascii_letters + string.digits):
    """
    Return random string upper and lower + digits
    """
    return ''.join(random.choice(chars) for i in xrange(size))

class UrlShortener(object):
    """
    Utils functions to make an integer to a short base 62 string and vice versa

    Thanks to https://gist.github.com/bhelx/778542 for this algo
    """
    # Constants
    BASE = 62
    UPPERCASE_OFFSET = 55
    LOWERCASE_OFFSET = 61
    DIGIT_OFFSET = 48

    SALT_LENGHT = 5

    @staticmethod
    def true_ord(char):
        """
        Turns a digit [char] in character representation
        from the number system with base [BASE] into an integer.
        """
        
        if char.isdigit():
            return ord(char) - UrlShortener.DIGIT_OFFSET
        elif 'A' <= char <= 'Z':
            return ord(char) - UrlShortener.UPPERCASE_OFFSET
        elif 'a' <= char <= 'z':
            return ord(char) - UrlShortener.LOWERCASE_OFFSET
        else:
            raise ValueError("%s is not a valid character" % char)

    @staticmethod
    def true_chr(integer):
        """
        Turns an integer [integer] into digit in base [BASE]
        as a character representation.
        """
        if integer < 10:
            return chr(integer + UrlShortener.DIGIT_OFFSET)
        elif 10 <= integer <= 35:
            return chr(integer + UrlShortener.UPPERCASE_OFFSET)
        elif 36 <= integer < 62:
            return chr(integer + UrlShortener.LOWERCASE_OFFSET)
        else:
            raise ValueError("%d is not a valid integer in the range of base %d" % (integer, UrlShortener.BASE))

    @staticmethod
    def _decode(key):
        """
        Turn the base [BASE] number [key] into an integer
        """
        int_sum = 0
        reversed_key = key[::-1]
        for idx, char in enumerate(reversed_key):
            int_sum += UrlShortener.true_ord(char) * int(math.pow(UrlShortener.BASE, idx))
        return int_sum

    @staticmethod
    def _encode(integer):
        """
        Turn an integer [integer] into a base [BASE] number
        in string representation
        """
        
        # we won't step into the while if integer is 0
        # so we just solve for that case here
        if integer == 0:
            return '0'
        
        string = ""
        while integer > 0:
            remainder = integer % UrlShortener.BASE
            string = UrlShortener.true_chr(remainder) + string
            integer /= UrlShortener.BASE
        return string

    @staticmethod
    def encode(integer):
        """ 
        Encode integer with random str(5)
        """
        short_url = UrlShortener._encode(integer)
        dump = random_str(UrlShortener.SALT_LENGHT)
        return (short_url + dump, dump)
    
    @staticmethod
    def decode(encoded, salt):
        """
        Remove salt and decode
        """
        short_url = encoded.replace(salt, '')
        return UrlShortener._decode(short_url)

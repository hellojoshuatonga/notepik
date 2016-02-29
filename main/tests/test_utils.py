"""
Test utils functions, class
"""
# Django
from django.test import TestCase

# Customs
from main.utils import UrlShortener, random_str

class UrlShortenerTest(TestCase):
    """ 
    Test case for UrlShortener utility class
    """
    def setUp(self):
        # Expected constants
        self.data = 123456789
        self.expected = '8M0kX'
    def test_can_encode(self):
        encoded, salt = UrlShortener.encode(123456789)
        self.assertEqual(encoded.replace(salt, ''), self.expected)
    def test_can_decode(self):
        encoded, salt = UrlShortener.encode(123456789)
        decoded = UrlShortener.decode(encoded, salt)
        self.assertEqual(decoded, self.data)
    def test_encode_string_throws_type_error(self):
        self.assertRaises(TypeError, UrlShortener.encode, "123456789")
    def test_decode_int_throws_type_error(self):
        self.assertRaises(TypeError, UrlShortener.decode, 123456789)

class UtilsFunctionTest(TestCase):
    """ 
    Test cases for utils functions
    """
    def test_random_str_correct_lenght(self):
        data = random_str(size=5)
        self.assertEqual(len(data), 5)

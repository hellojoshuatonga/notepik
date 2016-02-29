# Django
from django.test import TestCase
from django.core.urlresolvers import reverse

# Custom
from main.views import index
from main.models import NotepikUser

class IndexViewTest(TestCase):
    """
    Test case for the index view of main app
    """
    def setUp(self):
        self.key = NotepikUser.objects.create(email='test@email.com', key='testkey')
        self.index_url = reverse('main:index')
    def test_get_new_form(self):
        response = self.client.get(self.index_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Relax and take notes')

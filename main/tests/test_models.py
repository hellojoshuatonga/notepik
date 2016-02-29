# Django
from django.test import TestCase
from django.core.exceptions import ValidationError


# Custom
from main.models import Note, NotepikUser, Category, NoteReposter

class NoteModelTest(TestCase):
    """
    Test case for the Note model 
    """
    def setUp(self):
        # Create test datum
        self.author = NotepikUser.objects.create_user(email='test@email.com', password='testpass')
        self.reposter = NotepikUser.objects.create_user(email='test2@email.com', password='testkey2')
        self.note = Note.objects.create(note='Sample note #test #webapp', author=self.author)
    def test_extract_categories(self):
        categories = self.note.extract_categories()
        self.assertIn('test', categories)
        self.assertNotIn('note', categories)
    def test_categories_add(self):
        """
        Check if saving catogories model works
        """
        categories = [category.category for category in self.note.categories.all()]
        self.assertIn('test', categories)
        self.assertNotIn('note', categories)
    def test_reposters_add(self):
        NoteReposter.objects.create(note=self.note, user=self.reposter)
        self.assertIn(self.reposter, self.note.reposters.all())

class CategoryModelTest(TestCase):
    """
    Test case for the Category model 
    """
    def setUp(self):
        self.category = Category.objects.create(category="TEST")
    def test_category_lowercase(self):
        """ 
        Test if lowercase name
        """
        self.assertEqual(self.category.category, "test")
    def test_max_length_15(self):
        category = Category(category='12345sadsad67890123')
        self.assertGreater(category.category, 15)
        self.assertRaises(ValidationError, category.full_clean)

class NotepikUserModelTest(TestCase):
    """
    Test case for the NotepikUser model 
    """
    def setUp(self):
        self.user = NotepikUser.objects.create_user(email='testuser@email.com', password='testpassword')
    def test_key_is_password(self):
        self.assertEqual(self.user.key, 'testpassword')
    def test_user_short_name(self):
        self.assertEqual(self.user.get_short_name(), 'testuser')
    def test_user_full_name(self):
        self.assertEqual(self.user.get_full_name(), 'testuser@email.com')
    def test_set_password_new(self):
        self.user.set_password('newpassword')
        self.assertEqual(self.user.key, 'newpassword')
    def test_is_already_added(self):
        note = Note.objects.create(note='Hello', author=self.user)
        reposter = NotepikUser.objects.create_user(email='testreposter@email.com',
                password='testreposter')
        NoteReposter.objects.create(note=note, user=reposter)
        is_already_added = note.reposters.is_already_added(reposter)
        self.assertEqual(is_already_added, True)
    def test_not_already_added(self):
        note = Note.objects.create(note='Hello', author=self.user)
        reposter = NotepikUser.objects.create_user(email='testreposter@email.com',
                password='testreposter')
        is_already_added = note.reposters.is_already_added(reposter)
        self.assertEqual(is_already_added, False)

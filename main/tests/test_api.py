# Django
from django.contrib.auth import get_user_model
from django.utils.http import urlquote

# Rest framework
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.reverse import reverse

# Custom
from main.models import Note, EncodedUrl, NotepikUser, Category, NoteReposter

UserModel = get_user_model()


class NoteTest(APITestCase):
    """ 
    Test case for our Note model api
    """
    def setUp(self):
        self.user = UserModel.objects.create_user(
                email='test@email.com', password='testpass')
        self.notepikuser_url = reverse('main:notepikuser-detail', args=[self.user.pk])
        self.data = dict(note='Hello #test', author=self.notepikuser_url)


        self.user2 = UserModel.objects.create_user(email='test2@email.com', 
                password='test2pass')
        self.user2_url = reverse('main:notepikuser-detail', args=[self.user2.pk])

        self.data2 = dict(note='Hello test mo mukha mo #test', author=self.user2_url)

        self.token = str()
        self.list_url = 'main:note-list'
        self.detail_url = 'main:note-detail'

        print 'Email: {}'.format(self.user.email)
        print 'Client: {}'.format(self.client)
        print 'Token: {}'.format(self.token)
        print 'Data: {}'.format(self.data)
        print 'List url: {}'.format(self.list_url)
        print 'Reversed list url: {}'.format(reverse(self.list_url))
        print 'Detail url: {}'.format(self.detail_url)
        print 'Reversed detail url: {}'.format(reverse(self.detail_url, args=[1]))
    def get_token(self, key=False):
        if key:
            response = self.client.post(reverse('main:get-token'),
                    data=dict(key=key))
            return response.data.get('token')
        if not self.token:
            response = self.client.post(reverse('main:get-token'),
                    data=dict(key='testpass'))
            self.token = response.data.get('token')

        return self.token
    def create_note(self, data, token=False):
        if token:
            return self.client.post(reverse("main:note-list"), data, 
                    HTTP_AUTHORIZATION="JWT {}".format(token))
        else:
            return self.client.post(reverse("main:note-list"), data, 
                    HTTP_AUTHORIZATION="JWT {}".format(self.get_token()))
    def create_repost(self):
        encoded_url_resp = self.client.post(reverse("main:get-vault-url"),
                dict(key="testpass"))
        print encoded_url_resp.data

        encoded_url = EncodedUrl.objects.get(encoded_url=
                encoded_url_resp.data.get("encoded_url"))
        print encoded_url

        user = encoded_url.user
        print user

        notes_created_resp = self.create_note(self.data,
                self.get_token("testpass"))
        notes_others_created_resp = self.create_note(self.data2,
                self.get_token("testpass2"))

        # print notes_created_resp.data
        # print notes_others_created_resp.data
        note = Note.objects.get(pk=notes_others_created_resp.data.get('id'))
        NoteReposter(note=note, user=user)

        return (note, encoded_url_resp, user)
    def test_can_create_note(self):
        response = self.client.post(reverse(self.list_url), self.data,
                HTTP_AUTHORIZATION="JWT {}".format(self.get_token()))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    def test_can_update_note(self):
        note_response = self.create_note(self.data)
        updated_data = self.data
        updated_data.update(dict(note='Updated'))
        response = self.client.put(reverse(self.detail_url,
            args=[note_response.data.get('id')]), updated_data,
            HTTP_AUTHORIZATION="JWT {}".format(self.get_token()))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    def test_can_get_note_list(self):
        response = self.client.get(reverse(self.list_url))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    def test_can_get_note_detail(self):
        note_response = self.create_note(self.data)
        response = self.client.get(reverse(self.detail_url,
            args=[note_response.data.get('id')]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    def test_can_delete_note(self):
        note_response = self.create_note(self.data)
        response = self.client.delete(reverse(self.detail_url,
            args=[note_response.data.get('id')]),
            HTTP_AUTHORIZATION="JWT {}".format(self.get_token()))
        print "Token: {}".format(self.get_token())
        print note_response.data
        print response.data
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    def test_not_authenticated_can_get_note_list(self):
        response = self.client.get(reverse(self.list_url))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    def test_not_authenticated_cant_create_note(self):
        response = self.client.post(reverse(self.list_url), self.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    def test_not_authenticated_cant_update_note(self):
        self.create_note(self.data)
        updated_data = self.data
        updated_data.update(dict(note='Not updated'))
        response = self.client.put(reverse(self.detail_url, args=[1]), 
                updated_data)
    def test_not_authenticated_cant_delete_note(self):
        self.create_note(self.data)
        response = self.client.delete(reverse(self.detail_url, args=[1]))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    def test_add_to_vault(self):
        note_response = self.create_note(self.data)
        UserModel.objects.create_user(email='test3@email.com',
                password="testpass3")
        response = self.client.get(reverse('main:note-add-to-vault',
            args=[note_response.data.get('id')]),
            HTTP_AUTHORIZATION="JWT {}".format(self.get_token(key='testpass3')))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('result'), 'success')
    def test_cant_add_to_vault_if_same_author(self):
        note_response = self.create_note(self.data)
        response = self.client.get(reverse('main:note-add-to-vault',
            args=[note_response.data.get('id')]),
                HTTP_AUTHORIZATION="JWT {}".format(self.get_token()))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data.get('result'), 'you are the author')
    def test_not_authenticated_cant_add_to_vault(self):
        self.create_note(self.data)
        response = self.client.get(reverse('main:note-add-to-vault', args=[1]))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data.get('result'), 'not-authenticated')
    def test_remove_from_vault(self):
        note = Note.objects.create(note="test", author=self.user)
        reposter = UserModel.objects.create_user(email="testreposter@email.com",
                password="testreposter")
        NoteReposter.objects.create(note=note, user=reposter)
        response = self.client.get(reverse('main:note-remove-from-vault',
            args=[note.id]), HTTP_AUTHORIZATION="JWT {}".format(self.get_token(key=
                "testreposter")))
        print response.data
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('result'), 'removed from vault')
    def test_remove_author_from_note(self):
        note = Note.objects.create(note="test", author=self.user)
        response = self.client.get(reverse('main:note-remove-from-vault',
            args=[note.id]), HTTP_AUTHORIZATION="JWT {}".format(self.get_token()))
        print response.data
        self.assertEqual(response.status_code, 200)
    def test_no_category_length_greater_15(self):
        data = dict(note='asdsads #withveryverylongcategory',
                author=self.notepikuser_url)
        response = self.client.post(reverse('main:note-list'), data=data,
                HTTP_AUTHORIZATION="JWT {}".format(self.get_token()))
        print response.data
        self.assertEqual(response.status_code, 400)
    def test_delete_note_from_db_if_no_reposters_and_author(self):
        note = Note.objects.create(note="test", author=self.user)
        response = self.client.get(reverse("main:note-remove-from-vault",
            args=[note.id]), HTTP_AUTHORIZATION="JWT {}".format(self.get_token()))
        print response.data
        self.assertEqual(response.status_code, 200)
        with self.assertRaises(note.DoesNotExist):
            Note.objects.get(pk=note.id)
    def test_search_notes(self):
        self.create_repost()

        response = self.client.get(reverse("main:note-search"), data=dict(
            query="test"))
        print response.data

        self.assertEqual(response.status_code, 200)
    def test_search_notes_query_is_none(self):
        self.create_repost()

        response = self.client.get(reverse("main:note-search"), data=dict(
            query=""))
        print response.data

        self.assertEqual(response.status_code, 400)
    def test_search_notes_with_hashtag(self):
        self.create_repost()

        response = self.client.get(reverse("main:note-search"), data=dict(
            query="#test"))
        print response.data

        self.assertEqual(response.status_code, 200)
    def test_get_vault_notes(self):
        encoded_url_resp = self.client.post(reverse("main:get-vault-url"), data=
                dict(key="testpass"))

        print encoded_url_resp.data
        self.assertEqual(encoded_url_resp.status_code, 200)

        response = self.client.get(reverse("main:note-get-vault-notes"), data=
                dict(encoded_url=encoded_url_resp.data.get("encoded_url")))

        print response.data
        self.assertEqual(response.status_code, 200)

class CategoryTest(APITestCase):
    """ 
    Test case for our Category model api
    """
    def setUp(self):
        self.user = UserModel.objects.create_user(
                email='test@email.com', password='testpass')
        self.data = dict(category='Test #test', notes=[1])
        self.list_url = 'main:category-list'
        self.detail_url = 'main:category-detail'
        self.token = str()


        print 'Email: {}'.format(self.user.email)
        print 'Client: {}'.format(self.client)
        print 'Cookie: {}'.format(self.client.cookies)
        print 'Data: {}'.format(self.data)
        print 'List url: {}'.format(self.list_url)
        print 'Reversed list url: {}'.format(reverse(self.list_url))
        print 'Detail url: {}'.format(self.detail_url)
        print 'Reversed detaul url: {}'.format(reverse(self.detail_url, args=[1]))
    def get_token(self):
        if not self.token:
            response = self.client.post(reverse('main:get-token'), dict(key='testpass'))
            self.token = response.data.get('token')
        return self.token
    def create_note(self):
        return self.client.post(reverse('main:note-list'), data=
                dict(note='Hehehe #test', author=self.user.pk), HTTP_AUTHORIZATION=
                "JWT {}".format(self.get_token()))
    def create_note_category(self):
        return self.client.post(reverse(self.list_url), self.data,
                HTTP_AUTHORIZATION="JWT {}".format(self.get_token()))
    def test_can_create_note_category(self):
        self.create_note()
        response = self.create_note_category()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    def test_can_update_note_category(self):
        self.create_note()
        self.create_note_category()
        updated_data = self.data
        updated_data.update(dict(category='Updated category'))
        response = self.client.post(reverse(self.detail_url, args=[1]), updated_data)
    def test_can_get_note_category_list(self):
        self.create_note()
        self.create_note_category()
        response = self.client.get(reverse(self.list_url))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    def test_can_get_note_category_detail(self):
        self.create_note()
        category_response = self.create_note_category()
        response = self.client.get(reverse(self.detail_url,
            args=[category_response.data.get('id')]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    def test_can_delete_note_category(self):
        self.create_note()
        category_response = self.create_note_category()
        response = self.client.delete(reverse(self.detail_url,
            args=[category_response.data.get('id')]),
            HTTP_AUTHORIZATION="JWT {}".format(self.get_token()))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    def test_not_authenticated_can_get_note_category_list(self):
        self.create_note()
        self.create_note_category()
        response = self.client.get(reverse(self.list_url))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    def test_not_authenticated_can_get_note_category_detail(self):
        self.create_note()
        category_resp = self.create_note_category()
        response = self.client.get(reverse(self.detail_url,
            args=[category_resp.data.get('id')]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    def test_not_authenticated_cant_create_note_category(self):
        self.create_note()
        response = self.client.post(reverse(self.list_url), self.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    def test_not_authenticated_cant_update_note_category(self):
        self.create_note()
        self.create_note_category()
        updated_data = self.data
        updated_data.update(dict(category='Not updated'))
        response = self.client.put(reverse(self.detail_url, args=[1]), updated_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    def test_not_authenticated_cant_delete_note_category(self):
        self.create_note()
        self.create_note_category()
        response = self.client.delete(reverse(self.detail_url, args=[1]))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    def test_get_info_category(self):
        # note_resp = self.create_note();
        # print note_resp.data
        
        response = self.client.get(reverse("main:category-get-info"), data=dict(
            query=urlquote("test")))
        print response.data
        self.assertEqual(response.status_code, 200)

    def test_get_info_without_query_category(self):
        note_resp = self.create_note();
        print note_resp.data
        
        response = self.client.get(reverse("main:category-get-info"), data=dict(query=""))
        print response.data
        self.assertEqual(response.status_code, 400)
    def test_get_info_without_hashtag_category(self):
        note_resp = self.create_note();
        print note_resp.data
        
        response = self.client.get(reverse("main:category-get-info"), data=dict(quote=urlquote("test")))
        print response.data
        self.assertEqual(response.status_code, 200)

class VaultPageTest(APITestCase):
    def setUp(self):
        self.user = UserModel.objects.create_user(email='test@email.com', 
                password='testpass')
        self.user2 = UserModel.objects.create_user(email='test2@email.com', 
                password='test2pass')

        self.user_url = reverse('main:notepikuser-detail', args=[self.user.pk])
        self.user2_url = reverse('main:notepikuser-detail', args=[self.user2.pk])

        self.data = dict(note='Hello test test #test', author=self.user_url)
        self.data2 = dict(note='Hello test mo mukha mo #test', author=self.user2_url)

        self.token = str()
    def get_token(self, key=False):
        if key:
            response = self.client.post(reverse('main:get-token'),
                    data=dict(key=key))
            return response.data.get('token')
        if not self.token:
            response = self.client.post(reverse('main:get-token'),
                    data=dict(key='testpass'))
            self.token = response.data.get('token')

        return self.token
    def create_note(self, data, token=False):
        if token:
            return self.client.post(reverse("main:note-list"), data, 
                    HTTP_AUTHORIZATION="JWT {}".format(token))
        else:
            return self.client.post(reverse("main:note-list"), data, 
                    HTTP_AUTHORIZATION="JWT {}".format(self.get_token()))

    def test_get_encoded_url(self):
        response = self.client.post(reverse('main:get-vault-url'), 
                data=dict(key='testpass'))
        self.assertEqual(response.status_code, 200)
        response2 = self.client.get(reverse('main:vault',
            args=[response.data.get('encoded_url')]))
        self.assertEqual(response2.status_code, 200)
    def test_get_encoded_url_wrong_key(self):
        response = self.client.post(reverse("main:get-vault-url"), 
                data=dict(key='wrongkey'))
        self.assertEqual(response.status_code, 400)
    def test_search_api(self):
        encoded_url_resp = self.client.post(reverse("main:get-vault-url"),
                dict(key="testpass"))
        print encoded_url_resp.data

        encoded_url = EncodedUrl.objects.get(encoded_url=
                encoded_url_resp.data.get("encoded_url"))
        print encoded_url

        user = encoded_url.user
        print user

        notes_created_resp = self.create_note(self.data,
                self.get_token("testpass"))
        notes_others_created_resp = self.create_note(self.data2,
                self.get_token("testpass2"))

        # print notes_created_resp.data
        # print notes_others_created_resp.data
        note = Note.objects.get(pk=notes_others_created_resp.data.get('id'))
        NoteReposter(note=note, user=user)


        response = self.client.get(reverse("main:search-vault"),
                dict(encoded_url=encoded_url_resp.data.get("encoded_url"),
                    query="test"))
        print response.data
        self.assertEqual(response.status_code, 200)
    def test_search_api_wrong_data(self):
        response = self.client.get(reverse("main:search-vault"),
                dict(query="test"))
        print response.data
        self.assertEqual(response.status_code, 400)

class JsonAuthAPITest(APITestCase):
    def setUp(self):
        self.user = UserModel.objects.create_user(email="test@email.com", 
                password="testpass")
    def get_token(self, key=None):
        if key is None:
            response = self.client.post(reverse("main:get-token"), data=
                    dict(key=self.user.key))
        else:
            response = self.client.post(reverse("main:get-token"), data=
                    dict(key=key))

        return response.data.get("token", None)
    def test_correct_get_token(self):
        response = self.client.post(reverse("main:get-token"), 
                data=dict(key=self.user.key))
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.data.get("token"))
    def test_correct_verify_token(self):
        token = self.get_token()
        response = self.client.post(reverse("main:verify-token"), data=
                dict(token=token))
        print response.data
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get("token"), token)
    def test_correct_refresh_token(self):
        token = self.get_token()
        response = self.client.post(reverse("main:refresh-token"), data=
                dict(token=token))
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.data.get("token", None))
        self.token = response.data.get("token")
    def test_wrong_key_get_token(self):
        response = self.client.post(reverse("main:get-token"), data=
                dict(key="wrongkey"))
        self.assertEqual(response.status_code, 400)
    def test_wrong_token_verify_token(self):
        response = self.client.post(reverse("main:verify-token"), data=
                dict(token="wrongtoken"))
        self.assertEqual(response.status_code, 400)
    def test_wrong_token_refresh_token(self):
        response = self.client.post(reverse("main:refresh-token"), data=
                dict(token="wrongtoken"))
        self.assertEqual(response.status_code, 400)

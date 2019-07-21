from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from .models import Author


class AuthorTests(APITestCase):
    def setUp(self):
        self.USER_DATA = dict(
            username='testuser',
            password='test')
        self.AUTHOR_DATA = dict(
            user=self.USER_DATA,
            pseudonym='test author')

    def _run_basic_test(self, url):
        resp = self.client.post(
            url, self.AUTHOR_DATA, format='json')

        try:
            self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        except AssertionError as e:
            print(resp.data)
            raise e

        author = Author.objects.get(
            user__username=resp.data['user']['username'])
        user = User.objects.get(username=self.USER_DATA['username'])
        self.assertEqual(author.user, user)
        self.assertTrue(user.check_password(self.USER_DATA['password']))

    def _run_test_400(self, url):
        resp = self.client.post(
            url, self.AUTHOR_DATA, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_view_based_creation(self):
        url = reverse('examples:view-based-example')
        self._run_basic_test(url)

    def test_serializer_based_creation(self):
        url = reverse('examples:serializer-based-example')
        self._run_basic_test(url)

    def test_manager_backed_serializer_based_creation(self):
        url = reverse('examples:serializer-from-manager-based-example')
        self._run_basic_test(url)

    def test_view_double_creation(self):
        url = reverse('examples:view-based-example')
        self._run_basic_test(url)
        self._run_test_400(url)

    def test_serializer_double_creation(self):
        url = reverse('examples:serializer-based-example')
        self._run_basic_test(url)
        self._run_test_400(url)

    def test_serializer_from_manager_double_creation(self):
        url = reverse('examples:serializer-from-manager-based-example')
        self._run_basic_test(url)
        self._run_test_400(url)


class BookTests(APITestCase):
    def setUp(self):
        self.USER_DATA = dict(
            username='testuser',
            password='test')
        self.author = Author.objects.create_with_user(
            pseudonym='test author', **self.USER_DATA)

    def test_book_publish_from_serializer(self):


    def test_book_publish_model(self):
        pass

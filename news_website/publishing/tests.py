from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Users

# Create your tests here.


class ApiTests(APITestCase):

    def setUp(self):
        """
        This is the setup for tests in the tests python file
        """

        # create user
        self.token = ""
        self.article_id = ""
        self.newsletter_id = ""
        Users.objects.create_user(
            username="Testuser",
            first_name="Johnny",
            last_name="Test",
            email="15emiliomurray@gmail.com",
            password="password",
            editor=True,
            publisher=True,
            journalist=True,
        )

        # Login
        login_url = reverse("Api_Login")

        response = self.client.post(
            login_url,
            {
                "username": "Testuser",
                "password": "password",
            },
            format="json",
        )

        self.token = response.data["token"]

        # Create newsletter
        token = self.token
        title = "Test Newsletter"
        url = reverse("Api_Newsletter_Create")

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {token}"
        )

        response = self.client.post(
            url,
            {
                "title": title
            },
            format="json"
        )
        self.newsletter_id = response.data["id"]

        # Create article
        title = "Api test article title"
        url = reverse("Api_Article_Create")
        content = "This is the content of the article."

        response = self.client.post(
            url,
            {
                "news_letter_id": self.newsletter_id,
                "title": title,
                "content": content,
            },
            format="json"
        )

        self.article_id = response.data["id"]

    # api_login POST username password yes
    def test_api_login(self):
        """
        this function is used to test the login via api
        """
        login_url = reverse("Api_Login")

        login_response = self.client.post(
            login_url,
            {
                "username": "Testuser",
                "password": "password",
            },
            format="json",
        )

        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

    # api_news_letter_view GET id
    def test_news_letter_view(self):
        """
        This is used to test the api to view a newsletters articles
        """
        newsletter_id = self.newsletter_id
        url = reverse("Api_Newsletter_View")

        response = self.client.request(
            method="GET",
            url=url,
            data={
                "id": newsletter_id
            }
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # api_news_letter_subscribe POST id
    def test_api_newsletter_subscribe(self):
        """
        Testing the subscription to newsletters
        """
        token = self.token
        newsletter_id = self.newsletter_id
        url = reverse("Api_Newsletter_Sub")

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {token}"
        )

        response = self.client.request(
            method="POST",
            url=url,
            data={
                "id": newsletter_id
            }
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # api_view_subscriptions GET yes
    def test_api_views_subscriptions(self):
        """
        This is used to test if the api will return the correct response.
        When looking for the currently subscribed items.
        """

        token = self.token
        view_sub_url = reverse("Api_Subscriptions")

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {token}"
        )

        view_response = self.client.request(
            method="GET",
            url=view_sub_url,
        )

        self.assertEqual(view_response.status_code, status.HTTP_200_OK)

    # api_news_letter_unsubscribe POST id
    def test_api_newsletter_unsub(self):
        """
        Used to test the API's unsubscribe responses
        """

        token = self.token
        newsletter_id = self.newsletter_id
        url = reverse("Api_Newsletter_Unsub")

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {token}"
        )

        response = self.client.request(
            method="POST",
            url=url,
            data={
                "id": newsletter_id
            }
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # api_news_letter_view_all GET
    def test_api_newsletters_view_all(self):
        """
        This is used to test the api. And see if it shows all the current newsletters.
        """

        url = reverse("Api_Newsletter_View_All")

        response = self.client.request(
            method="POST",
            url=url,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # api_article GET id
    def test_api_article_detailed(self):
        """
        This is a test for the api to see if a detailed version of the article is returned
        """

        token = self.token
        article_id = self.article_id
        url = reverse("Api_Article")

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {token}"
        )

        response = self.client.request(
            method="GET",
            url=url,
            data={
                "id": article_id
            }
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # api_news_letter_edit PUT id
    def test_api_newsletter_edit(self):
        """
        This is a test for the api to see if it can edit the newsletter
        """

        token = self.token
        newsletter_id = self.newsletter_id
        new_title = "api new title test"
        url = reverse("Api_Newsletter_Edit")

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {token}"
        )

        response = self.client.request(
            method="PUT",
            url=url,
            data={
                "id": newsletter_id,
                "title": new_title,
            }
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # api_article_edit PUT id title content
    def test_api_article_edit(self):
        """
        This is used to test the api to see if it can edit an article
        """

        token = self.token
        article_id = self.article_id
        new_title = "Jeff"
        content = "My name Jeff"
        url = reverse("Api_Article_Edit")

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {token}"
        )

        response = self.client.request(
            method="PUT",
            url=url,
            data={
                "id": article_id,
                "title": new_title,
                "content": content
            }
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # api_article_delete DELETE id
    def test_api_article_delete(self):
        """
        This is a test of the api to see if the api can delete an article
        """

        token = self.token
        article_id = self.article_id
        url = reverse("Api_Article_Delete")

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {token}"
        )

        response = self.client.request(
            method="DELETE",
            url=url,
            data={
                "id": article_id,
            }
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # api_news_letter_delete DELETE id
    def test_api_newsletter_delete(self):
        """
        This test is to test if the api can delete a newsletter
        """

        token = self.token
        newsletter_id = self.newsletter_id
        url = reverse("Api_Article_Delete")

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {token}"
        )

        response = self.client.request(
            method="DELETE",
            url=url,
            data={
                "id": newsletter_id,
            }
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

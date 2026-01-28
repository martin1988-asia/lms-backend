from django.test import TestCase, Client
from django.urls import reverse, resolve
from lms_backend import urls


class UrlsTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_home_view(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("Welcome to Martin's backend", response.content.decode())

    def test_dashboard_urls_resolve(self):
        for name in [
            "student-dashboard",
            "instructor-dashboard",
            "admin-dashboard",
            "api-student-dashboard",
            "api-instructor-dashboard",
            "api-admin-dashboard",
        ]:
            path = reverse(name)
            match = resolve(path)
            self.assertEqual(match.view_name, name)

    def test_auth_urls_resolve(self):
        for name in [
            "custom_token_obtain_pair",
            "custom_token_refresh",
            "token_obtain_pair",
            "token_refresh",
            "signup",
            "api_auth_token_obtain_pair",
            "api_auth_token_refresh",
            "api_token_obtain_pair",
            "api_token_refresh",
        ]:
            path = reverse(name)
            match = resolve(path)
            self.assertEqual(match.view_name, name)

    def test_swagger_urls_resolve(self):
        for name in [
            "schema-json",
            "schema-yaml",
            "schema-swagger-ui",
            "schema-redoc",
        ]:
            path = reverse(name)
            match = resolve(path)
            self.assertEqual(match.view_name, name)

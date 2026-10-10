from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class TestingUtilityAccessTests(TestCase):
    def test_testing_utilities_require_authentication(self):
        response = self.client.get(reverse("testing:testing"))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse("accounts:login")))

    def test_authenticated_user_can_still_use_testing_utilities(self):
        user = get_user_model().objects.create_user(
            username="test-user",
            password="not-used-for-force-login",
        )
        self.client.force_login(user)
        self.assertEqual(self.client.get(reverse("testing:testing")).status_code, 200)
        self.assertEqual(
            self.client.get(reverse("testing:say_hello", args=("visitor",))).status_code,
            200,
        )

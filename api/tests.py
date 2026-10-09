from unittest.mock import patch

from django.db import DatabaseError
from django.urls import reverse
from rest_framework.test import APITestCase

from .models import User


class TestUserView(APITestCase):
    def setUp(self):
        self.user = User.objects.create(name="Test1", dni="09876543210")
        self.url = reverse("users-list")
        self.detail = reverse("users-detail", args=[self.user.pk])
        self.data = {"name": "Test2", "dni": "09876543211"}

    def test_post(self):
        response = self.client.post(self.url, self.data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {"id": self.user.pk + 1, **self.data})
        self.assertEqual(User.objects.count(), 2)

    def test_get_list(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(), [{"id": self.user.pk, "name": "Test1", "dni": "09876543210"}]
        )

    def test_get(self):
        response = self.client.get(self.detail)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["name"], "Test1")

    def test_duplicate(self):
        response = self.client.post(
            self.url, {"name": "Other", "dni": self.user.dni}, format="json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"detail": "User already exists"})
        self.assertEqual(User.objects.count(), 1)

    def test_invalid_payloads(self):
        for data in [
            {},
            {"name": "", "dni": "123"},
            {"name": "x" * 31, "dni": "123"},
            {"name": "Valid", "dni": "1" * 14},
        ]:
            with self.subTest(data=data):
                self.assertEqual(self.client.post(self.url, data, format="json").status_code, 400)
        self.assertEqual(User.objects.count(), 1)

    def test_not_found(self):
        self.assertEqual(self.client.get(reverse("users-detail", args=[999999])).status_code, 404)

    def test_patch(self):
        response = self.client.patch(self.detail, {"name": "Updated"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, "Updated")

    def test_delete(self):
        self.assertEqual(self.client.delete(self.detail).status_code, 204)
        self.assertEqual(User.objects.count(), 0)

    def test_model_string(self):
        self.assertEqual(str(self.user), "Test1")

    def test_liveness_independent_of_database(self):
        with patch("api.health.connection.cursor", side_effect=DatabaseError):
            self.assertEqual(self.client.get("/health/live/").status_code, 200)

    def test_readiness(self):
        self.assertEqual(self.client.get("/health/ready/").json(), {"status": "ready"})

    def test_readiness_failure(self):
        with patch("api.health.connection.cursor", side_effect=DatabaseError):
            response = self.client.get("/health/ready/")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json(), {"status": "unavailable"})

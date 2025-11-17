from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from django.utils import timezone

from api.models import WaterUnit, WaterQuality, Maintenance, Maintainer


class APITest(APITestCase):

    def setUp(self):
        # ---------------------------
        # 1. Register a maintainer
        # ---------------------------
        register_url = reverse("register")

        payload = {
            "username": "testuser",
            "name": "testuser",
            "password": "pass1234",
            "email": "test@example.com"
        }

        res = self.client.post(register_url, payload, format="json")
        self.assertEqual(
            res.status_code, 200,
            f"Register failed: {res.status_code} {res.data}"
        )

        token = res.data["token"]
        self.maintainer_id = res.data["maintainer_id"]

        # Login not needed — token already created, but still test login below

        # Set authentication header for protected endpoints
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")


    # -------------------------------------------------------------------
    #                          AUTH TESTS
    # -------------------------------------------------------------------

    def test_register(self):
        """Ensure registration works"""
        url = reverse("register")
        res = self.client.post(url, {
            "username": "user2",
            "password": "pass1234",
            "email": "user2@example.com",
        }, format="json")

        self.assertEqual(res.status_code, 200)
        self.assertIn("token", res.data)
        self.assertIn("maintainer_id", res.data)

    def test_login(self):
        """Ensure login returns token + user info"""
        url = reverse("login")
        res = self.client.post(url, {
            "username": "testuser",
            "password": "pass1234",
        }, format="json")

        self.assertEqual(res.status_code, 200)
        self.assertIn("token", res.data)
        self.assertEqual(res.data["username"], "testuser")


    # -------------------------------------------------------------------
    #                       WATER UNIT CRUD TESTS
    # -------------------------------------------------------------------

    def test_water_unit_crud(self):
        # CREATE
        res = self.client.post("/api/water-unit/", {
            "name": "Unit A",
            "location": "Block 1"
        }, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        unit_id = res.data["id"]

        # RETRIEVE
        res = self.client.get(f"/api/water-unit/{unit_id}/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["name"], "Unit A")

        # UPDATE
        res = self.client.patch(f"/api/water-unit/{unit_id}/", {
            "location": "Block 2"
        }, format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["location"], "Block 2")

        # DELETE
        res = self.client.delete(f"/api/water-unit/{unit_id}/")
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)


    # -------------------------------------------------------------------
    #                   WATER QUALITY FILTER + ORDERING TEST
    # -------------------------------------------------------------------

    def test_water_quality_filters_and_ordering(self):
        # Create a unit
        unit = WaterUnit.objects.create(name="Unit 1", location="Area 1")

        # Create water quality entries
        WaterQuality.objects.create(wu=unit, tds=100, date_time=timezone.now())
        WaterQuality.objects.create(wu=unit, tds=300, date_time=timezone.now())

        # Filter tds >= 200
        res = self.client.get("/api/water-quality/?min_tds=200")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["tds"], 300)

        # Test ordering
        res = self.client.get("/api/water-quality/?ordering=-tds")
        self.assertEqual(res.status_code, 200)
        self.assertGreaterEqual(res.data[0]["tds"], res.data[-1]["tds"])


    # -------------------------------------------------------------------
    #                  MAINTENANCE AUTH + FILTER TEST
    # -------------------------------------------------------------------

    def test_maintenance_auth_and_filter(self):
        # Create a unit
        unit = WaterUnit.objects.create(name="Unit X", location="Loc Y")

        # CREATE maintenance record
        res = self.client.post("/api/maintenance/", {
            "wu": unit.id,
            "maintainer": self.maintainer_id,
            "problem": "Motor issue"
        }, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # FILTER maintenance by problem_contains
        res = self.client.get("/api/maintenance/?problem_contains=motor")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 1)

        # FILTER by date
        today = timezone.now().date().isoformat()
        res = self.client.get(f"/api/maintenance/?date={today}")
        self.assertEqual(res.status_code, 200)


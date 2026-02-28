import json
from unittest.mock import patch, MagicMock
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from account.models import PlatformUser
from profile_player.models import PlayerProfile
from game.models import Game
from common.constants import LocationClientType, GameType
from location.models import Location, LocationSharingSetting


class LocationAPITests(APITestCase):
    def setUp(self):
        # Create a user and profile
        self.user = PlatformUser.create(email="test@qyaar.com", phone="1234567890")
        self.profile = PlayerProfile.create(platform_user=self.user, profile_name="Test Profile")
        
        # Create game master profile
        from profile_game_master.models import GameMasterProfile
        self.gm_profile = GameMasterProfile.create(platform_user=self.user, profile_name="Game Master")
        
        # Create a game
        self.game = Game.create(
            game_type=GameType.HIDE_N_SEEK, 
            name="Test Game", 
            description="A test game", 
            created_by=self.gm_profile
        )

        self.valid_payload = {
            "game_id": str(self.game.external_id),
            "client": LocationClientType.WEB_APP.name,
            "locations": [
                {
                    "lat": 12.345678,
                    "lon": 98.765432,
                    "accuracy": 10.5,
                    "timestamp": "2026-02-28T10:00:00Z"
                },
                {
                    "lat": 12.345679,
                    "lon": 98.765433,
                    "accuracy": 5.0,
                    "timestamp": "2026-02-28T10:01:00Z"
                }
            ]
        }

    def authenticate(self):
        mock_jwt_decode = patch("common.decorators.jwt.decode").start()
        mock_get_profile = patch("common.decorators.svc_auth_get_profile_for_user_and_role").start()
        
        mock_jwt_decode.return_value = {"role": "PLAYER", "user_id": str(self.user.external_id)}
        mock_get_profile.return_value = (None, self.profile)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer mock_token")
        
        # Mock request user for test client
        self.client.force_authenticate(user=self.user)
        
        self.addCleanup(patch.stopall)

    def test_add_locations_success(self):
        self.authenticate()

        url = reverse("location:location-pings")
        response = self.client.post(url, data=json.dumps(self.valid_payload), content_type="application/json")
        
        # print error if we get 400
        if response.status_code == 400:
            print("Response:", response.json())

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Location.objects.count(), 2)

    def test_add_locations_missing_client(self):
        self.authenticate()

        payload = self.valid_payload.copy()
        payload.pop("client")

        url = reverse("location:location-pings")
        response = self.client.post(url, data=json.dumps(payload), content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_enable_sharing_and_update_tracking_code(self):
        self.authenticate()

        url = reverse("location:location-sharing-settings")
        response = self.client.post(url, data={"is_sharing_enabled": True}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        setting = LocationSharingSetting.objects.get(player=self.profile)
        self.assertTrue(setting.is_sharing_enabled)
        self.assertIsNotNone(setting.tracking_code)

    def test_reset_sharing_and_tracking_code(self):
        self.authenticate()

        # First enable sharing to generate a tracking code
        url = reverse("location:location-sharing-settings")
        self.client.post(url, data={"is_sharing_enabled": True}, format="json")
        setting = LocationSharingSetting.objects.get(player=self.profile)
        self.assertTrue(setting.is_sharing_enabled)
        self.assertIsNotNone(setting.tracking_code)
        
        # Now hit the reset endpoint
        reset_url = reverse("location:location-sharing-reset")
        reset_response = self.client.post(reset_url, format="json")
        
        self.assertEqual(reset_response.status_code, status.HTTP_200_OK)
        setting.refresh_from_db()
        self.assertFalse(setting.is_sharing_enabled)
        self.assertIsNone(setting.tracking_code)

    def test_get_locations_success(self):

        # Create setting so filtering works
        setting, _ = LocationSharingSetting.objects.get_or_create(player=self.profile)
        setting.is_sharing_enabled = True
        setting.save()

        # Add some setup locations manually
        loc1 = Location.create(
            player=self.profile, game=self.game, team=None,
            lat=10.0, lon=20.0, timestamp="2026-02-28T10:00:00Z", client=LocationClientType.ANDROID
        )
        loc2 = Location.create(
            player=self.profile, game=self.game, team=None,
            lat=11.0, lon=21.0, timestamp="2026-02-28T11:00:00Z", client=LocationClientType.ANDROID
        )
        
        self.authenticate()

        url = reverse("location:location-pings")
        response = self.client.get(url, {"game_id": str(self.game.external_id)})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Depending on if it uses standard pagination or standard response, response.data varies
        # Assuming standard paginated format here:
        results = response.data.get("results", response.data)
        if isinstance(results, dict) and "data" in results:
            results = results["data"]["results"]
        elif isinstance(results, dict) and "results" in results:
            results = results["results"]
            
        print("Results length:", len(results))
        if len(results) == 0:
            print("Response:", response.json())
        
        # Both records added via payload AND the ones created manually should appear for this game
        # Order should be descending by reported time
        self.assertTrue(len(results) >= 2)

    def test_get_locations_missing_filter(self):
        self.authenticate()

        url = reverse("location:location-pings")
        response = self.client.get(url)  # No game_id, team_id or player_id provided
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_last_location_success(self):
        # Create a location
        loc = Location.create(
            player=self.profile, game=self.game, team=None,
            lat=22.0, lon=33.0, timestamp="2026-02-28T12:00:00Z", client=LocationClientType.ANDROID
        )
        
        # Ensure sharing is ON
        setting, _ = LocationSharingSetting.objects.get_or_create(player=self.profile)
        setting.is_sharing_enabled = True
        setting.save()
        
        self.authenticate()

        url = reverse("location:player-last-location")
        response = self.client.get(url, {"player_ids": str(self.profile.platform_user.external_id)})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        results = response.data
        if "data" in results:
            results = results["data"]
            
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["external_id"], str(loc.external_id))
        
    def test_get_last_location_sharing_disabled(self):
        self.authenticate()
        
        # Disable sharing
        setting, _ = LocationSharingSetting.objects.get_or_create(player=self.profile)
        setting.is_sharing_enabled = False
        setting.save()

        url = reverse("location:player-last-location")
        response = self.client.get(url, {"player_ids": str(self.profile.platform_user.external_id)})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        results = response.data
        if "data" in results:
            results = results["data"]
            
        self.assertEqual(len(results), 0)

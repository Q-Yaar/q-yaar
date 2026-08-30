import uuid
from unittest.mock import patch

from django.test import TestCase

from account.models import PlatformUser
from common.constants import AssetStatus, GameType, GameVisibilityMode, UserRolesType
from game.models import Game
from media.models import Asset
from media.services.core import (
    svc_media_confirm_upload,
    svc_media_get_assets,
    svc_media_get_download_url,
    svc_media_request_upload,
)
from media.services.error_codes import ErrorCode


def _make_game(code: str = "GTEST1") -> Game:
    return Game.objects.create(
        game_type=GameType.HIDE_N_SEEK.value,
        game_visibility_mode=GameVisibilityMode.PRIVATE.value,
        game_code=code,
        name="Test Game",
        description="desc",
    )


def _make_user(email: str = "user@test.invalid") -> PlatformUser:
    return PlatformUser.objects.create_user(external_id=uuid.uuid4(), email=email)


# Storage is an external system; the driver calls are stubbed so no S3 is
# needed. The presign helpers import lazily, so patch the module attribute.
PRESIGN_PUT = "common.storage.presign_put_url"
PRESIGN_GET = "common.storage.presign_get_url"


class RequestUploadTest(TestCase):
    def setUp(self):
        self.user = _make_user()
        self.game = _make_game()

    @patch(PRESIGN_PUT, return_value="https://s3/put")
    def test_creates_pending_asset_and_returns_put_url(self, _mock_put):
        data = {"game_id": str(self.game.external_id), "asset_name": "photo.jpg", "content_type": "image/jpeg"}

        error, response = svc_media_request_upload(data, self.user, UserRolesType.PLAYER)

        self.assertEqual(error.code, ErrorCode.CREATED)
        self.assertEqual(response["upload_url"], "https://s3/put")
        self.assertIn("object_key", response)

        asset = Asset.objects.get(external_id=uuid.UUID(response["asset_id"]))
        self.assertEqual(asset.status, AssetStatus.PENDING.value)
        self.assertEqual(asset.asset_name, "photo.jpg")
        self.assertEqual(asset.game, self.game)
        self.assertEqual(asset.role, UserRolesType.PLAYER.value)
        # key is namespaced under the game prefix
        self.assertTrue(asset.object_key.startswith(f"games/{self.game.external_id}/PLAYER/"))

    def test_missing_game_id(self):
        error, _ = svc_media_request_upload({"asset_name": "x"}, self.user, UserRolesType.PLAYER)
        self.assertEqual(error.code, ErrorCode.MISSING_GAME_ID)

    def test_missing_asset_name(self):
        error, _ = svc_media_request_upload({"game_id": str(self.game.external_id)}, self.user, UserRolesType.PLAYER)
        self.assertEqual(error.code, ErrorCode.MISSING_ASSET_NAME)

    def test_invalid_game_id(self):
        error, _ = svc_media_request_upload(
            {"game_id": str(uuid.uuid4()), "asset_name": "x"}, self.user, UserRolesType.PLAYER
        )
        self.assertEqual(error.code, ErrorCode.INVALID_GAME_ID)


class ConfirmUploadTest(TestCase):
    def setUp(self):
        self.user = _make_user()
        self.game = _make_game()
        self.asset = Asset.create(
            external_id=uuid.uuid4(),
            uploaded_by=self.user,
            role=UserRolesType.PLAYER,
            game=self.game,
            object_key="games/x/PLAYER/y/z",
            asset_name="a.jpg",
        )

    def test_flips_status_to_uploaded(self):
        error, _ = svc_media_confirm_upload(self.asset.external_id)
        self.assertEqual(error.code, ErrorCode.SUCCESS)
        self.asset.refresh_from_db()
        self.assertEqual(self.asset.status, AssetStatus.UPLOADED.value)

    def test_double_confirm_is_conflict(self):
        svc_media_confirm_upload(self.asset.external_id)
        error, _ = svc_media_confirm_upload(self.asset.external_id)
        self.assertEqual(error.code, ErrorCode.ASSET_ALREADY_UPLOADED)

    def test_invalid_asset_id(self):
        error, _ = svc_media_confirm_upload(uuid.uuid4())
        self.assertEqual(error.code, ErrorCode.INVALID_ASSET_ID)


class DownloadUrlTest(TestCase):
    def setUp(self):
        self.user = _make_user()
        self.game = _make_game()
        self.asset = Asset.create(
            external_id=uuid.uuid4(),
            uploaded_by=self.user,
            role=UserRolesType.PLAYER,
            game=self.game,
            object_key="games/x/PLAYER/y/z",
            asset_name="a.jpg",
        )

    @patch(PRESIGN_GET, return_value="https://s3/get")
    def test_returns_get_url_when_uploaded(self, _mock_get):
        self.asset.status = AssetStatus.UPLOADED.value
        self.asset.save()

        error, response = svc_media_get_download_url(self.asset.external_id)
        self.assertEqual(error.code, ErrorCode.SUCCESS)
        self.assertEqual(response["download_url"], "https://s3/get")
        self.assertEqual(response["asset_name"], "a.jpg")

    def test_rejects_download_when_not_uploaded(self):
        error, _ = svc_media_get_download_url(self.asset.external_id)
        self.assertEqual(error.code, ErrorCode.ASSET_NOT_UPLOADED)

    def test_invalid_asset_id(self):
        error, _ = svc_media_get_download_url(uuid.uuid4())
        self.assertEqual(error.code, ErrorCode.INVALID_ASSET_ID)


class GetAssetsTest(TestCase):
    def setUp(self):
        self.user = _make_user()
        self.game = _make_game()
        self.other_game = _make_game(code="GTEST2")
        Asset.create(
            external_id=uuid.uuid4(),
            uploaded_by=self.user,
            role=UserRolesType.PLAYER,
            game=self.game,
            object_key="k1",
            asset_name="a",
        )
        Asset.create(
            external_id=uuid.uuid4(),
            uploaded_by=self.user,
            role=UserRolesType.PLAYER,
            game=self.other_game,
            object_key="k2",
            asset_name="b",
        )

    def test_lists_all_when_no_filter(self):
        error, assets = svc_media_get_assets({}, serialized=False)
        self.assertEqual(error.code, ErrorCode.SUCCESS)
        self.assertEqual(assets.count(), 2)

    def test_filters_by_game(self):
        error, assets = svc_media_get_assets({"game_id": str(self.game.external_id)}, serialized=False)
        self.assertEqual(error.code, ErrorCode.SUCCESS)
        self.assertEqual(assets.count(), 1)
        self.assertEqual(assets.first().game, self.game)

    def test_invalid_game_id(self):
        error, _ = svc_media_get_assets({"game_id": str(uuid.uuid4())})
        self.assertEqual(error.code, ErrorCode.INVALID_GAME_ID)
